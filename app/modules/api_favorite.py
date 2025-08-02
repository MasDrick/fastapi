import modules.constants as constants
import modules.database.query_api as database

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/favorite",
    tags=["favorite"]
)

@router.get("/")
def get_favorite(user_id: int):
    """
    Получает список избранных моделей пользователя
    """
    favorites = database.get_user_favorites(user_id)
    if favorites:
        return favorites
    else:
        raise HTTPException(status_code=404, detail="Нет избранных моделей для данного пользователя")

@router.post("/add")
def add_favorite(
    user_id: int,
    model_name: str    
):
    """
    Получает название модели и добавляет в таблицу, выводит новую коллекцию избранных
    """

    if (model_name not in constants.text_models) and (model_name not in constants.image_models):
        raise HTTPException(status_code=400, detail="Неверная модель")

    if database.add_favorite_model(user_id, model_name):
        return {"message": "Модель успешно добавлена в избранное"}
    else:
        raise HTTPException(status_code=500, detail="Ошибка при добавлении модели в избранное")

@router.delete("/delete")
def del_favorite(
    user_id: int,
    model_name: str
):
    """
    Удаляет модель из избранного пользователя
    """
    if database.del_model(user_id, model_name):
        return {"message": "Модель успешно удалена из избранного"}
    else:
        raise HTTPException(status_code=500, detail="Ошибка при удалении модели из избранного")
