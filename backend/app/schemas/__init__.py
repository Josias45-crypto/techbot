# --------------------------------------------------
# Registro central de todos los esquemas Pydantic
# Importar desde aquí en los endpoints: 
# from backend.app.schemas import UserResponse, ProductResponse
# --------------------------------------------------

# Usuarios y autenticación
from backend.app.schemas.user import (
    RoleCreate, RoleResponse,
    UserCreate, UserUpdate, UserResponse, UserWithRole,
    LoginRequest, TokenResponse,
    SessionResponse
)

# Catálogo e inventario
from backend.app.schemas.catalog import (
    CategoryCreate, CategoryResponse,
    BrandCreate, BrandResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductDetail,
    ProductSpecCreate, ProductSpecResponse,
    InventoryUpdate, InventoryResponse,
    CompatibilityCreate, CompatibilityResponse
)

# Drivers y base de conocimiento
from backend.app.schemas.knowledge import (
    DriverCreate, DriverUpdate, DriverResponse,
    KnownIssueCreate, KnownIssueUpdate, KnownIssueResponse,
    FAQCreate, FAQUpdate, FAQResponse,
    KnowledgeEmbeddingResponse
)

# Chatbot y conversaciones
from backend.app.schemas.chatbot import (
    IntentCreate, IntentResponse,
    ConversationCreate, ConversationResponse,
    MessageCreate, MessageResponse,
    ChatInput, ChatResponse,
    EscalationResponse,
    MessageIntentResponse
)

# Tickets
from backend.app.schemas.tickets import (
    TicketCreate, TicketUpdate, TicketResponse, TicketWithHistory,
    TicketHistoryCreate, TicketHistoryResponse
)

# Pedidos y reparaciones
from backend.app.schemas.orders import (
    OrderCreate, OrderUpdate, OrderResponse, OrderWithItems,
    OrderItemCreate, OrderItemResponse,
    RepairCreate, RepairUpdate, RepairResponse, RepairWithHistory,
    RepairHistoryCreate, RepairHistoryResponse,
    WaitlistCreate, WaitlistResponse
)

# Métricas y auditoría
from backend.app.schemas.metrics import (
    AuditLogCreate, AuditLogResponse,
    MetricsDailyResponse,
    DashboardSummary
)
