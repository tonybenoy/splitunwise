from fastapi import Depends, FastAPI


from sqlalchemy.orm import Session

from src.model import Expense, Payment, Split, User, get_db
from src.pydantic_models import ExpenseNew, PaymentNew, UserNew

app = FastAPI()


@app.get("/test")
async def test():
    return {
        "result": "success",
        "message": "It works!",
    }


@app.post("/create_user")
async def create_user(user: UserNew, db: Session = Depends(get_db)):
    newUser = User(name=user.name)

    db.add(newUser)
    db.commit()
    return {
        "result": "success",
        "message": "User Created!",
    }


@app.post("/get_user")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        return {"result": "error", "message": "User not found!", "data": {}}

    return {"result": "success", "message": "User found!", "data": user}


@app.post("/create_expense")
async def create_expense(expense: ExpenseNew, db: Session = Depends(get_db)):
    amount_due = 0
    split_users = []
    for split in expense.splits:
        if split.amount <= 0:
            return {
                "result": "error",
                "message": "Split amount should always be positive or non zero!",
            }
        amount_due += split.amount
        split_users.append(split.user_id)
    split_users.append(expense.user_id)
    if abs(amount_due) > expense.amount:
        return {
            "result": "success",
            "message": "Sum of splits cannot be greater than total spent!",
        }
    user_count = db.query(User).filter(User.id.in_(split_users)).count()
    if user_count != len(split_users):
        return {
            "result": "success",
            "message": "Users provided do not exist!",
        }
    newExpense = Expense(
        amount=expense.amount, user_ids=split_users, paid_by=expense.user_id
    )
    db.add(newExpense)
    db.flush()
    for split in expense.splits:
        newSplit = Split(
            expense_id=newExpense.id, user_id=split.user_id, amount=split.amount
        )
        db.add(newSplit)
    db.commit()
    return {
        "result": "success",
        "message": "Expense Created!",
    }


@app.post("/create_payment")
async def create_payment(payment: PaymentNew, db: Session = Depends(get_db)):
    if payment.amount <= 0:
        return {
            "result": "error",
            "message": "Amount has to be greater than zero!",
        }
    user_count = (
        db.query(User).filter(User.id.in_((payment.user_id, payment.paid_to))).count()
    )
    if user_count != 2:
        return {
            "result": "success",
            "message": "Users provided do not exist!",
        }
    newPayment = Payment(
        amount=payment.amount, user_id=payment.user_id, paid_to=payment.paid_to
    )
    db.add(newPayment)
    db.commit()
    return {
        "result": "success",
        "message": "Payment recorded!",
    }


@app.post("/fetch_statement")
async def get_amount_owed(user_id: int, db: Session = Depends(get_db)):
    resp = db.execute(
        """
    select
        paid_by as owed_to,
        s.user_id as owed_by,
        sum(coalesce (s.amount,0))-sum(coalesce (p.amount,0)) as amount
    from
        split s
    join expense e on
        s.expense_id = e.id
    left join payment p on
        p.paid_to = paid_by
        and s.user_id = p.user_id
    where
        s.user_id = :user_id
    group by
        1,
        2""",
        {"user_id": user_id},
    ).all()
    return {"result": "success", "message": "Statment fetch!", "data": resp}


@app.post("/fetch_owed")
async def get_owed(user_id: int, db: Session = Depends(get_db)):
    resp = db.execute(
        """
        select
            paid_by,
            sum(coalesce (s.amount,0))-sum(coalesce (p.amount,0))
        from
            split s
        join expense e on
            s.expense_id = e.id
        left join payment p on
            p.paid_to = paid_by
            and s.user_id = p.user_id
        where
            paid_by=:user_id
        group by
            1""",
        {"user_id": user_id},
    ).all()
    return {"result": "success", "message": "Owed amount!", "data": resp}
