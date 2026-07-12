from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.admin_anon import router as admin_anon_router
from handlers.admin_antispam import router as admin_antispam_router
from handlers.admin_buttons import router as admin_buttons_router
from handlers.admin_msg import router as admin_msg_router
from handlers.admin_stats import router as admin_stats_router
from handlers.user import router as user_router
from handlers.relay import router as relay_router

from tools import tools_routers

all_routers = [
    start_router,
    admin_router,
    admin_anon_router,
    admin_antispam_router,
    admin_buttons_router,
    admin_msg_router,
    admin_stats_router,
    user_router,
] + tools_routers + [
    relay_router,
]
