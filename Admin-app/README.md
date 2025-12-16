# Admin Portal - Login Interface

Giao diện đăng nhập admin được clone chính xác 100% từ trang tham chiếu, với thiết kế tối giản, sang trọng và chuyên nghiệp.

## Tính năng

- ✅ Giao diện đăng nhập clone 100% tỷ lệ 1:1
- ✅ Background gradient động với particle effects
- ✅ Glassmorphism card với hiệu ứng blur và gradient border
- ✅ Form validation và error handling
- ✅ Responsive design cho mobile và desktop
- ✅ Custom checkbox styling
- ✅ Security badge và footer

## Cài đặt

### 1. Cài đặt dependencies

```bash
cd Admin-app
npm install
```

### 2. Chạy development server

```bash
npm run dev
```

Ứng dụng sẽ chạy tại `http://localhost:3001`

### 3. Build cho production

```bash
npm run build
```

## Cấu trúc dự án

```
Admin-app/
├── src/
│   ├── assets/
│   │   ├── fonts/          # Font files
│   │   ├── icons/           # Icon assets
│   │   └── images/          # Image assets
│   ├── components/
│   │   └── ParticleBackground.vue  # Background với particle effects
│   ├── views/
│   │   └── LoginPage.vue    # Trang đăng nhập chính
│   ├── router/
│   │   └── index.js         # Vue Router configuration
│   ├── styles/
│   │   └── main.css         # Global styles
│   ├── App.vue              # Root component
│   └── main.js              # Entry point
├── public/                  # Static assets
├── index.html               # HTML entry
├── package.json             # Dependencies
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── postcss.config.js       # PostCSS configuration
```

## Technologies

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Next generation frontend tooling
- **Tailwind CSS** - Utility-first CSS framework
- **Font Awesome** - Icon library
- **Remixicon** - Icon library
- **Vue Router** - Official router for Vue.js

## Assets

- **Fonts**: Secular One, Pacifico (via Google Fonts CDN)
- **Icons**: Font Awesome 6.4.0, Remixicon 4.5.0 (via CDN)

## Styling

Giao diện sử dụng:
- Dark theme với gradient background (slate-900 → indigo-900)
- Glassmorphism effects với backdrop-blur
- Custom gradient buttons (blue → purple)
- Particle animation trên background
- Responsive breakpoints cho mobile và desktop

## Tích hợp Backend

✅ **Đã hoàn thành tích hợp 100% với FastAPI Backend**

### API Endpoints đã tích hợp:

1. **Authentication** (`/api/auth`)
   - Login, Logout, Token Refresh

2. **User Management** (`/api/admin/users`)
   - List users, User details, Update user status, Bulk operations

3. **Dashboard** (`/api/admin/dashboard`, `/api/admin/platform/stats`)
   - Real-time statistics, System health, Recent activities

4. **Trading Management** (`/api/admin/trades`)
   - List trades, Approve/Reject trades, Batch approval

5. **Financial Management** (`/api/admin/deposits`, `/api/admin/withdrawals`)
   - Deposit/Withdrawal management, Approval workflows

6. **Analytics** (`/api/admin/analytics`)
   - KPIs, Charts, Top assets, User insights

7. **System Settings** (`/api/admin/settings`)
   - General, Security, Trading, Notification settings

8. **Admin Trading Controls** (`/api/admin/trading-adjustments`)
   - Win rate control, Position override

### Environment Configuration

Tạo file `.env` với nội dung:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Trong Docker, biến môi trường được inject tại build time qua `docker-compose.yml`.

### Docker Deployment

```bash
# Build và chạy với Docker Compose
docker-compose build admin-app
docker-compose up -d admin-app
```

Ứng dụng sẽ chạy tại `http://localhost:3001/admin/`

## License

MIT

