class RecordBookInteractionUseCase:
    def __init__(self, interactions_repo) -> None:
        self._repo = interactions_repo

    def execute_impression(self, book_id: int, telegram_id: int | None = None) -> None:
        self._repo.record_impression(book_id=book_id, telegram_id=telegram_id)

    def execute_click(self, book_id: int, telegram_id: int | None = None) -> None:
        self._repo.record_click(book_id=book_id, telegram_id=telegram_id)

