from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from app import db
from datetime import datetime
from sqlalchemy.orm import backref
from models import BookingStatus



class Payment(db.Model):
    # __abstract__ = True
    __tablename__ = 'payments'

    # @declared_attr
    # def __tablename__(cls):
    #     return cls.__name__.lower()
    
    id = db.Column(db.Integer, primary_key=True)
    originalAmount = db.Column(db.Float, nullable=False)
    discountedAmount = db.Column(db.Float, nullable=False)
    createdOn = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(50))
    couponId = db.Column(db.String, db.ForeignKey('coupons.id'))

    # @declared_attr
    # def coupon(cls):
        # return
    coupon = relationship('Coupon', backref='payments')
    # bookingId = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    
    # @declared_attr
    # def booking(cls):
    #     return 
    booking = relationship('Booking', back_populates='payment', uselist=False)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'payment'
    }

    def calcDiscount(self) -> float:
        discount = 0
        if self.coupon and Coupon.couponIsValid(self.coupon.code):
            discount += self.coupon.discount
        return discount

    def calcFinalPayment(self) -> float:
        return self.originalAmount * (1 - self.calcDiscount())
    
    @staticmethod
    def createPayment(payment: "Payment") -> "Payment":
        payment.discountedAmount = payment.calcFinalPayment()
        db.session.add(payment)

        payment.booking.status = BookingStatus.CONFIRMED

        payment.booking.payment = payment

        db.session.commit()
        
        payment.booking.sendNotification()
        return payment
    
    @staticmethod
    def getPaymentById(paymentId: int) -> "Payment":
        return Payment.query.get(paymentId)
    
class CreditCard(Payment):
    __tablename__ = 'creditcards'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    creditCardNumber = db.Column(db.String, nullable=False)
    expiryDate = db.Column(db.String, nullable=False)
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
    change = db.Column(db.Float, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'cash'
    }

    def calcChange(self) -> float:
        return self.receivedCash - self.discountedAmount

class Eftpos(Payment):
    __tablename__ = 'eftpos'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'eftpos'
    }

class Coupon(db.Model):
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    expiryDate = db.Column(db.DateTime, nullable=False)
    discount = db.Column(db.Float, nullable=False)

    # @staticmethod
    # def createCoupon(data: dict) -> "Coupon":
    #     coupon = Coupon(**data)
    #     db.session.add(coupon)
    #     db.session.commit()
    #     return coupon
    
    @staticmethod
    def getCouponByCode(code: str) -> "Coupon":
        if Coupon.couponIsValid(code):
            return Coupon.query.filter(code == Coupon.code).first()
        else:
            return None

    @staticmethod
    def couponIsValid(code: str) -> bool:
        existingCoupon = Coupon.query.filter(code == Coupon.code).first()
        if not existingCoupon:
            return False
        if existingCoupon.expiryDate < datetime.now():
            return False
        return True


class Refund(db.Model):
    __tablename__ = 'refunds'

    id = db.Column(db.Integer, primary_key=True)
    paymentId = db.Column(db.Integer, db.ForeignKey('payments.id'))
    payment = relationship('Payment', backref=backref('refunds', uselist=False))
    amount = db.Column(db.Float, nullable=False)
    processedOn = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reason = db.Column(db.String, nullable=False)
    
    @staticmethod
    def createRefund(paymentId: int, amount: float, reason: str) -> "Refund":
        refund = Refund(paymentId=paymentId, amount=amount, reason=reason)
        db.session.add(refund)
        db.session.commit()
        return refund