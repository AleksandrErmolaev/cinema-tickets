from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db, engine
from models import Base, Payment, PaymentStatus
from schemas import PaymentResponse, PaymentInitiateRequest
from kafka_producer import start_kafka_producer, stop_kafka_producer, send_payment_event
from kafka_consumer import consume_booking_events
import asyncio
import uuid
from datetime import datetime

app = FastAPI(title="Payment Service")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await start_kafka_producer()
    asyncio.create_task(consume_booking_events())

@app.on_event("shutdown")
async def shutdown():
    await stop_kafka_producer()

@app.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def initiate_payment(request: PaymentInitiateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Payment).where(Payment.booking_id == request.booking_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Payment already processed")
    
    payment = Payment(
        booking_id=request.booking_id,
        amount=request.amount,
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    
    import random
    success = random.random() < 0.8
    if success:
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()
        await db.commit()
        await send_payment_event(request.booking_id, "completed")
    else:
        payment.status = PaymentStatus.FAILED
        await db.commit()
        await send_payment_event(request.booking_id, "failed")
    
    await db.refresh(payment)
    return PaymentResponse(
        id=payment.id,
        booking_id=payment.booking_id,
        amount=payment.amount,
        status=payment.status,
        created_at=payment.created_at,
        completed_at=payment.completed_at
    )

@app.get("/payments/booking/{booking_id}", response_model=PaymentResponse)
async def get_payment_by_booking(booking_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Payment).where(Payment.booking_id == booking_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse(
        id=payment.id,
        booking_id=payment.booking_id,
        amount=payment.amount,
        status=payment.status,
        created_at=payment.created_at,
        completed_at=payment.completed_at
    )