"""
Bot Management Service
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.db.models import Bot
from app.core.config import settings

logger = logging.getLogger(__name__)

class BotManager:
    """Manages multiple Telegram bot instances"""
    
    def __init__(self):
        self.active_bots: Dict[int, asyncio.Task] = {}
        self.bot_instances: Dict[int, any] = {}
    
    async def start_bot(self, db: Session, bot_id: int) -> bool:
        """Start a bot by its ID"""
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            logger.error(f"Bot with ID {bot_id} not found")
            return False
        
        if bot_id in self.active_bots:
            logger.warning(f"Bot {bot.name} is already running")
            return False
        
        try:
            # Import aiogram here to avoid startup errors
            from aiogram import Bot as AioBot, Dispatcher, types
            from aiogram.utils import executor
            
            # Create bot instance
            telegram_bot = AioBot(token=bot.token)
            dp = Dispatcher(telegram_bot)
            
            # Basic start command handler
            @dp.message_handler(commands=['start'])
            async def cmd_start(message: types.Message):
                await message.answer(
                    f"👋 Hello! I am {bot.name}.\n"
                    f"I am managed by Master Bot Control Panel.\n\n"
                    f"Use /help to see available commands."
                )
            
            @dp.message_handler(commands=['help'])
            async def cmd_help(message: types.Message):
                await message.answer(
                    f"🤖 <b>{bot.name} Commands:</b>\n\n"
                    f"/start - Start the bot\n"
                    f"/help - Show this help message\n"
                    f"/status - Check bot status\n\n"
                    f"<i>Managed by Master Bot System</i>",
                    parse_mode='HTML'
                )
            
            @dp.message_handler(commands=['status'])
            async def cmd_status(message: types.Message):
                await message.answer(
                    f"✅ <b>{bot.name}</b> is running!\n\n"
                    f"Bot ID: {bot.id}\n"
                    f"Status: Active\n"
                    f"Admin: Master Control Panel",
                    parse_mode='HTML'
                )
            
            @dp.message_handler()
            async def echo(message: types.Message):
                await message.answer(
                    f"📝 You said: {message.text}\n\n"
                    f"Use /help to see available commands."
                )
            
            # Store instance
            self.bot_instances[bot_id] = (telegram_bot, dp)
            
            # Create async task
            async def run_polling():
                try:
                    await dp.start_polling()
                except Exception as e:
                    logger.error(f"Bot {bot.name} polling error: {e}")
                    self._set_error_status(db, bot_id)
            
            task = asyncio.create_task(run_polling())
            self.active_bots[bot_id] = task
            
            # Update database
            bot.is_active = True
            bot.status = "running"
            bot.started_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Bot {bot.name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bot {bot.name}: {e}")
            self._set_error_status(db, bot_id)
            return False
    
    async def stop_bot(self, db: Session, bot_id: int) -> bool:
        """Stop a bot by its ID"""
        if bot_id not in self.active_bots:
            logger.warning(f"Bot with ID {bot_id} is not running")
            return False
        
        try:
            # Cancel the task
            task = self.active_bots[bot_id]
            task.cancel()
            
            # Close bot instance
            if bot_id in self.bot_instances:
                telegram_bot, dp = self.bot_instances[bot_id]
                await telegram_bot.session.close()
                del self.bot_instances[bot_id]
            
            # Remove from active bots
            del self.active_bots[bot_id]
            
            # Update database
            bot = db.query(Bot).filter(Bot.id == bot_id).first()
            if bot:
                bot.is_active = False
                bot.status = "stopped"
                bot.started_at = None
                db.commit()
            
            logger.info(f"Bot stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop bot {bot_id}: {e}")
            return False
    
    async def restart_bot(self, db: Session, bot_id: int) -> bool:
        """Restart a bot by its ID"""
        await self.stop_bot(db, bot_id)
        await asyncio.sleep(1)  # Brief pause
        return await self.start_bot(db, bot_id)
    
    def _set_error_status(self, db: Session, bot_id: int):
        """Set bot status to error"""
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if bot:
            bot.is_active = False
            bot.status = "error"
            db.commit()
    
    def get_active_bots_count(self) -> int:
        """Get count of active bots"""
        return len(self.active_bots)
    
    async def stop_all_bots(self, db: Session):
        """Stop all running bots"""
        bot_ids = list(self.active_bots.keys())
        for bot_id in bot_ids:
            await self.stop_bot(db, bot_id)
        logger.info("All bots stopped")

# Global bot manager instance
bot_manager = BotManager()
