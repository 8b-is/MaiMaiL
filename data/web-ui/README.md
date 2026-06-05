# MaiMaiL Modern Web UI 🚀

A beautiful, AI-powered web interface for MaiMaiL (Mailcow) built with SvelteKit and TypeScript.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![SvelteKit](https://img.shields.io/badge/SvelteKit-FF3E00?logo=svelte&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-38B2AC?logo=tailwind-css&logoColor=white)

## 🎨 Features

### Core Features
- ✨ **Modern SvelteKit Architecture** - Fast, reactive, and type-safe
- 🎨 **Beautiful UI Components** - Built with TailwindCSS v4
- 🌙 **Dark Mode Support** - Automatic theme detection and manual toggle
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- 🔒 **TypeScript** - Full type safety throughout the application

### AI Intelligence Features (⭐ **NEW**)
- 🤖 **Real-time LLM Monitoring** - View AI analysis statistics and health status
- 📧 **Email Analysis Display** - Show AI-generated summaries, categories, and priority scores
- 🎣 **Phishing Detection Alerts** - Visual warnings for potentially malicious emails
- 🔐 **Sensitive Data Warnings** - Automatic detection of passwords, credit cards, etc.
- 💬 **Auto-Reply Suggestions** - AI-powered response recommendations
- ⭐ **Priority Scoring** - Intelligent email prioritization (1-10 scale)
- 🏷️ **Smart Categorization** - Automatic tagging (work, personal, finance, urgent, etc.)

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

Visit http://localhost:5173 to see the dashboard!

## 📸 Screenshots

### Dashboard with AI Intelligence
Beautiful overview with real-time LLM monitoring, system stats, and health indicators.

### AI Email Analysis
Every email analyzed with:
- 📝 AI-generated summary (2-3 sentences)
- 🏷️ Smart categories (work, personal, urgent, etc.)
- ⭐ Priority score (1-10)
- 🎣 Phishing detection with confidence score
- 🔐 Sensitive data warnings
- 💬 Suggested replies

## 🏗️ Project Structure

```
src/
├── routes/                     # Pages
│   ├── +layout.svelte         # Main layout with navigation
│   └── +page.svelte           # Dashboard with LLM monitoring
├── lib/
│   ├── api/                   # API client for json_api.php
│   ├── components/
│   │   ├── ui/                # Base components (Button, Card, Badge, etc.)
│   │   ├── llm/               # LLM-specific components
│   │   └── layout/            # Layout components (Header, etc.)
│   ├── stores/                # State management (auth, theme, notifications)
│   ├── types/                 # TypeScript definitions
│   └── utils/                 # Helper functions
└── app.css                    # Global styles
```

## 📡 API Integration

Connects seamlessly to existing Mailcow `/json_api.php` endpoint with:
- ✅ Automatic retry logic with exponential backoff
- ✅ Session management
- ✅ Type-safe API methods
- ✅ Comprehensive error handling

### Supported Endpoints
- **Authentication**: Login, logout, auth status
- **Mailboxes**: CRUD operations for mailboxes
- **Domains**: Domain management
- **LLM**: Email analysis, stats, health, configuration
- **Quarantine**: Spam/phishing management

## ✅ Completed Features

### Phase 1: Foundation ✅
- [x] SvelteKit setup with TypeScript
- [x] TailwindCSS v4 integration
- [x] Component library
- [x] Dark mode
- [x] API client with retry logic
- [x] State management

### Phase 2: AI Dashboard ✅
- [x] System overview dashboard
- [x] LLM health monitoring
- [x] Statistics visualization
- [x] Recent analyses feed
- [x] AI analysis card components
- [x] Phishing indicators
- [x] Priority scoring

## 🚧 Roadmap

### Phase 3: Mailbox Management
- [ ] Mailbox list with search/filters
- [ ] Create/edit forms
- [ ] Quota visualization

### Phase 4: Email Viewer
- [ ] Email list with AI summaries
- [ ] Detail view with analysis
- [ ] Phishing warnings
- [ ] Smart filtering

### Phase 5: LLM Config Panel
- [ ] System settings
- [ ] User preferences
- [ ] Model selection
- [ ] Performance tuning

### Phase 6: Advanced
- [ ] WebSocket real-time updates
- [ ] Smart compose
- [ ] Chart visualizations
- [ ] Export functionality

## 🎨 Design System

### Colors
- **Primary** (Blue): Main actions, links
- **Success** (Green): Healthy status, successful operations
- **Warning** (Amber): Degraded status, warnings
- **Danger** (Red): Phishing, errors, critical alerts
- **Secondary** (Slate): Backgrounds, subtle elements

### Components
All components support:
- Multiple sizes (sm, md, lg)
- Multiple variants (primary, secondary, success, warning, danger)
- Dark mode
- Accessibility (ARIA labels, keyboard navigation)

## 🔧 Development

```bash
npm run dev          # Development server (http://localhost:5173)
npm run build        # Production build
npm run preview      # Preview production build
npm run check        # TypeScript type checking
npm run check:watch  # Watch mode for type checking
```

## 🐛 Troubleshooting

### API Connection Issues
- Verify `VITE_API_BASE_URL` in `.env`
- Check CORS configuration on backend
- Inspect Network tab in browser DevTools

### Build Errors
- Ensure `@tailwindcss/postcss` is installed
- Run `npm run check` for TypeScript issues
- Clear `.svelte-kit` directory and rebuild

## 📦 Deployment

### Docker (Recommended)
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
```

### Nginx Integration
```nginx
location /ui/ {
    alias /opt/mailcow/data/web-ui/build/;
    try_files $uri $uri/ /ui/index.html;
}
```

## 📝 Tech Stack

- **Framework**: SvelteKit
- **Language**: TypeScript
- **Styling**: TailwindCSS v4
- **Build Tool**: Vite
- **Date Handling**: date-fns
- **Charts**: Chart.js (planned)

## 🤝 Contributing

Contributions are welcome! Please:
1. Create a feature branch
2. Make changes with proper types
3. Test thoroughly
4. Submit PR with clear description

## 📄 License

Part of MaiMaiL/Mailcow - GNU General Public License v3.0

---

**Built with ❤️ using SvelteKit, TypeScript, and TailwindCSS**

Visit the [main repository](https://github.com/8b-is/MaiMaiL) for more information.
