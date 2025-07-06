# Conga CPQ Troubleshooting Frontend

A modern React frontend for the Conga CPQ Turbo API troubleshooting chatbot.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Backend API running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at: http://localhost:3000

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── MessageRenderer.tsx
│   │   └── LoadingIndicator.tsx
│   ├── services/           # API service layer
│   │   └── api.ts
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # React entry point
│   └── index.css           # Global styles with Tailwind
├── public/                 # Static assets
├── package.json
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## 🎨 Features

### Core Functionality
- **Real-time Chat**: Interactive conversation with the AI assistant
- **Markdown Support**: Rich text rendering for API documentation
- **Code Highlighting**: Syntax highlighting for code blocks
- **API Execution**: Dynamic API calls with bearer token support
- **Connection Status**: Real-time connection monitoring
- **Error Handling**: Comprehensive error reporting and recovery

### UI/UX Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode Ready**: Prepared for dark mode implementation
- **Loading States**: Interactive loading indicators and animations
- **Copy to Clipboard**: Easy copying of responses and code
- **Suggested Actions**: Smart follow-up question suggestions
- **Token Management**: Secure bearer token input workflow

### Technical Features
- **TypeScript**: Full type safety and IntelliSense
- **React 18**: Latest React features and optimizations
- **Vite**: Fast development and optimized builds
- **Tailwind CSS**: Utility-first styling with custom design system
- **Axios**: Robust HTTP client with interceptors
- **ESLint**: Code quality and consistency

## 🛠️ Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues automatically
```

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
```

### Customization

#### Styling
- Modify `tailwind.config.js` to customize the design system
- Edit `src/index.css` for global styles
- Use Tailwind utility classes for component styling

#### API Integration
- Update `src/services/api.ts` for API endpoints
- Modify `src/types/index.ts` for data models
- Configure proxy in `vite.config.ts` for development

#### Components
- Add new components in `src/components/`
- Update `MessageRenderer.tsx` for custom markdown rendering
- Modify `LoadingIndicator.tsx` for different loading states

## 🔧 Configuration

### Vite Configuration
The `vite.config.ts` includes:
- React plugin for JSX support
- Development server on port 3000
- Proxy configuration for API calls
- Build optimizations

### Tailwind Configuration
Custom design system with:
- Primary color palette
- Custom animations and keyframes
- Extended spacing and typography
- Responsive breakpoints

### TypeScript Configuration
Strict TypeScript setup with:
- Latest ES2020 features
- React JSX support
- Strict type checking
- Module resolution optimization

## 📱 Responsive Design

The application is fully responsive and works across:
- **Desktop**: Full-featured experience with sidebar and detailed views
- **Tablet**: Optimized layout with touch-friendly interactions
- **Mobile**: Streamlined interface with gesture support

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Deployment Options

#### Static Hosting (Recommended)
- **Vercel**: Zero-config deployment with automatic builds
- **Netlify**: Easy deployment with form handling and redirects
- **GitHub Pages**: Free hosting for open source projects

#### Traditional Hosting
- **Nginx**: Configure as a static file server
- **Apache**: Use with mod_rewrite for SPA routing
- **CDN**: Deploy to any CDN for global distribution

### Environment Configuration

For production deployment, set the API URL:

```bash
VITE_API_URL=https://your-api-domain.com
```

## 🧪 Testing

The project is set up for testing with:
- Jest for unit testing
- React Testing Library for component testing
- Cypress for end-to-end testing (can be added)

## 🔒 Security

Security considerations implemented:
- **Input Sanitization**: All user inputs are properly sanitized
- **HTTPS**: Enforced in production environments
- **Token Security**: Bearer tokens are handled securely
- **CORS**: Proper CORS configuration with the backend
- **Content Security Policy**: Ready for CSP implementation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.