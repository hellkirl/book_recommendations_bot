from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from core.domain.model.rating import Rating
from core.ports.rating_repository import IRatingRepository
from ..database import SessionLocal
from ..orm_models import RatingORM


class RatingRepository(IRatingRepository):
    def get_ratings(self, telegram_id: int) -> list[Rating]:
        with SessionLocal() as session:
            rows = (
                session.execute(
                    select(RatingORM)
                    .where(RatingORM.telegram_id == telegram_id)
                    .order_by(RatingORM.created_at.desc())
                )
                .scalars()
                .all()
            )
            return [_to_domain(r) for r in rows]

    def save_rating(self, rating: Rating) -> None:
        with SessionLocal() as session:
            stmt = (
                sqlite_insert(RatingORM)
                .values(
                    telegram_id=rating.telegram_id,
                    book_id=rating.book_id,
                    score=rating.score,
                    created_at=rating.created_at or datetime.utcnow(),
                )
                .on_conflict_do_update(
                    index_elements=["telegram_id", "book_id"],
                    set_={"score": rating.score, "created_at": datetime.utcnow()},
                )
            )
            session.execute(stmt)
            session.commit()

    def count_ratings(self, telegram_id: int) -> int:
        with SessionLocal() as session:
            return session.execute(
                select(func.count())
                .select_from(RatingORM)
                .where(RatingORM.telegram_id == telegram_id)
            ).scalar_one()

    def get_rated_book_ids(self, telegram_id: int) -> set[int]:
        with SessionLocal() as session:
            rows = (
                session.execute(
                    select(RatingORM.book_id).where(
                        RatingORM.telegram_id == telegram_id
                    )
                )
                .scalars()
                .all()
            )
            return set(rows)


def _to_domain(row: RatingORM) -> Rating:
    return Rating(
        telegram_id=row.telegram_id,
        book_id=row.book_id,
        score=row.score,
        created_at=row.created_at,
    )
