from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from ..database import db
from typing import Tuple
from datetime import datetime
from sqlalchemy.orm import backref
from ..models import BookingStatus


# Payment class/table
class Payment(db.Model):

    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    originalAmount = db.Column(db.Float, nullable=False)
    discountedAmount = db.Column(db.Float, nullable=False)
    createdOn = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(50))
    couponId = db.Column(db.String, db.ForeignKey('coupons.id'))

    coupon = relationship('Coupon', backref='payments')

    booking = relationship('Booking', back_populates='payment', uselist=False)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'payment'
    }

    # method to calculate discount
    def calcDiscount(self) -> float:
        discount = 0
        if self.coupon and Coupon.couponIsValid(self.coupon.code):
            discount += self.coupon.discount
        return discount

    # method to calculate final amount after discount
    def calcFinalPayment(self) -> float:
        return self.originalAmount * (1 - self.calcDiscount())
    
    # method to create payment object and add to database
    @staticmethod
    def createPayment(payment: "Payment") -> Tuple[bool, str]:
        # if payment exist and already paid, return false
        existingPayment = Payment.query.filter(Payment.booking == payment.booking)
        if existingPayment and payment.booking.status == BookingStatus.CONFIRMED:
            return False, "Already paid."
        payment.discountedAmount = round(payment.calcFinalPayment(), 2)
        db.session.add(payment)

        # if payment successful, change the booking's status to confirmed
        payment.booking.status = BookingStatus.CONFIRMED

        # add the payment to the booking
        payment.booking.payment = payment

        db.session.commit()
        
        # after payment successful, send notification to the customer
        payment.booking.sendNotification()
        return True, "Payment successful."
    
    # method to get the payment by id
    @staticmethod
    def getPaymentById(paymentId: int) -> "Payment":
        return Payment.query.get(paymentId)

# CreditCard class/table  
class CreditCard(Payment):
    __tablename__ = 'creditcards'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    creditCardNumber = db.Column(db.String, nullable=False)
    expiryDate = db.Column(db.String, nullable=False)
    nameOnCard = db.Column(db.String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'creditcard'
    }

# DebitCard class/table
class DebitCard(Payment):
    __tablename__ = 'debitcards'
    
    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    cardNumber = db.Column(db.String, nullable=False)
    bankName = db.Column(db.String, nullable=False)
    nameOnCard = db.Column(db.String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'debitcard'
    }

# CashPayment class/table
class CashPayment(Payment):
    __tablename__ = 'cashPayments'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    receivedCash = db.Column(db.Float, nullable=False)  # Amount of cash received from the customer
    change = db.Column(db.Float, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'cash'
    }

    # method to calculate amount of change
    def calcChange(self) -> float:
        return self.receivedCash - self.discountedAmount

# Eftpos class/table
class Eftpos(Payment):
    __tablename__ = 'eftpos'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'eftpos'
    }

# Coupon class/table
class Coupon(db.Model):
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    expiryDate = db.Column(db.DateTime, nullable=False)
    discount = db.Column(db.Float, nullable=False)
    
    # method to get coupon by code
    @staticmethod
    def getCouponByCode(code: str) -> "Coupon":
        if Coupon.couponIsValid(code):
            return Coupon.query.filter(code == Coupon.code).first()
        else:
            return None

    # method to check if coupon is valid
    @staticmethod
    def couponIsValid(code: str) -> bool:
        # check if the same code exists in the database
        existingCoupon = Coupon.query.filter(code == Coupon.code).first()
        if not existingCoupon:
            return False
        # check if coupon expired
        if existingCoupon.expiryDate < datetime.now():
            return False
        return True

# Refunc class/table
class Refund(db.Model):
    __tablename__ = 'refunds'

    id = db.Column(db.Integer, primary_key=True)
    paymentId = db.Column(db.Integer, db.ForeignKey('payments.id'))
    payment = relationship('Payment', backref=backref('refunds', uselist=False))
    amount = db.Column(db.Float, nullable=False)
    processedOn = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reason = db.Column(db.String, nullable=False)
    
    # method to create a refund object in database
    @staticmethod
    def createRefund(paymentId: int, amount: float, reason: str) -> "Refund":
        refund = Refund(paymentId=paymentId, amount=amount, reason=reason)
        db.session.add(refund)
        db.session.commit()
        return refund