"""Umumiy handlerlar: /start, yordam, balans, asosiy menyu."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app import texts
from app.falcon_api import FalconAPI, FalconAPIError
from app.keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    name = message.from_user.full_name if message.from_user else "do'stim"
    await message.answer(
        texts.WELCOME.format(name=name),
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(texts.HELP_TEXT, reply_markup=main_menu())


@router.message(F.text == "ℹ️ Yordam")
async def btn_help(message: Message) -> None:
    await message.answer(texts.HELP_TEXT, reply_markup=main_menu())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.MAIN_MENU_TITLE, reply_markup=main_menu())


@router.message(F.text == "💰 Balans")
async def show_balance(message: Message, api: FalconAPI) -> None:
    try:
        data = await api.balance()
    except FalconAPIError as exc:
        await message.answer(texts.API_ERROR.format(error=exc))
        return

    await message.answer(
        texts.BALANCE_TEXT.format(
            balance=data.get("balance", "—"),
            currency=data.get("currency", ""),
        )
    )
