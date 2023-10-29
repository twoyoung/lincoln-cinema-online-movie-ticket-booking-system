from sqlalchemy.orm import relationship
from app import db
from datetime import datetime
from sqlalchemy.orm import backref
from models import BookingStatus



class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    originalAmount = db.Column(db.Float, nullable=False)
    discountedAmount = db.Column(db.Float, nullable=False)
    createdOn = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(50))
    coupon = relationship('Coupon', backref='payments')
    bookingId = db.Column(db.Integer, db.ForeignKey('bookings.bookingId'))
    booking = relationship('Booking', backref=backref('payment', uselist=False))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'payment'
    }

    def calcDiscount(self) -> float:
        discount = 0
        if self.coupon and self.coupon.expiryDate > datetime.now():
            discount += self.coupon.discount
        return discount

    def calcFinalPayment(self) -> float:
        return self.originalAmount * (1 - self.calcDiscount())
    
    @staticmethod
    def createPayment(payment: "Payment") -> "Payment":
        payment.discountedAmount = payment.calcFinalPayment()
        db.session.add(payment)
        db.session.commit()
        payment.booking.status = BookingStatus.CONFIRMED
        payment.booking.payment = payment
        payment.booking.sendNotification()
        return payment
    
    @staticmethod
    def getPaymentById(paymentId: int) -> "Payment":
        return Payment.query.get(paymentId)
    
class CreditCard(Payment):
    __tablename__ = 'creditcards'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    creditCardNumber = db.Column(db.String, nullable=False)
    expiryDate = db.Column(db.DateTime, nullable=False)
    nameOnCard = db.Column(db.String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'creditcard'
    }


class DebitCard(Payment):
    __tablename__ = 'debitcards'
    
    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    cardNumber = db.Column(db.String, nullable=False)
    bankName = db.Column(db.String, nullable=False)
    nameOnCard = db.Column(db.String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'debitcard'
    }

class CashPayment(Payment):
    __tablename__ = 'cashPayments'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    receivedCash = db.Column(db.Float, nullable=False)  # Amount of cash received from the customer
    
    __mapper_args__ = {
        'polymorphic_identity': 'cash'
    }

    def calChange(self) -> float:
        return self.receivedCash - self.discountedAmount

class Eftpos(Payment):
    __tablename__ = 'eftpos'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    method = db.Column(db.String(50), nullable=False)  # This can be 'creditcard' or 'debitcard'
    
    __mapper_args__ = {
        'polymorphic_identity': 'eftpos'
    }

class Coupon(db.Model):
    __tablename__ = 'coupons'
    
    couponID = db.Column(db.String, primary_key=True)
    expiryDate = db.Column(db.DateTime, nullable=False)
    discount = db.Column(db.Float, nullable=False)

    # @staticmethod
    # def createCoupon(data: dict) -> "Coupon":
    #     coupon = Coupon(**data)
    #     db.session.add(coupon)
    #     db.session.commit()
    #     return coupon
    
    # @staticmethod
    # def getCouponById(couponId: str) -> "Coupon":
    #     return Coupon.query.get(couponId)


class Refund(db.Model):
    __tablename__ = 'refunds'

    id = db.Column(db.Integer, primary_key=True)
    paymentId = db.Column(db.Integer, db.ForeignKey('payments.id'))
    payment = relationship('Payment', backref=backref('refund', uselist=False))
    amount = db.Column(db.Float, nullable=False)
    processedOn = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reason = db.Column(db.String, nullable=False)
    
    @staticmethod
    def createRefund(paymentId: int, amount: float, reason: str) -> "Refund":
        refund = Refund(paymentId=paymentId, amount=amount, reason=reason)
        db.session.add(refund)
        db.session.commit()
        return refund