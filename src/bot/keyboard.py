from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

goal = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Weight loss',
                callback_data='Weight loss'
            ),
            InlineKeyboardButton(
                text='Maintaining weight',
                callback_data='Maintaining weight'
            ),
            InlineKeyboardButton(
                text='Mass gain',
                callback_data='Mass gain'
            ),
        ]
    ]
)

activity = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Almost complete lack of physical activity',
                callback_data='1.2'
            )
        ],
        [
            InlineKeyboardButton(
                text='Low level of physical activity',
                callback_data='1.375'
            )
        ],
        [
            InlineKeyboardButton(
                text='Average level of physical activity',
                callback_data='1.55'
            )
        ],
        [
            InlineKeyboardButton(
                text='Above average physical activity level',
                callback_data='1.725'
            )
        ],
        [
            InlineKeyboardButton(
                text='High level of physical activity',
                callback_data='1.9'
            ),
        ]
    ]
)

history = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="History by day", callback_data="history_by_days")]
    ]
)