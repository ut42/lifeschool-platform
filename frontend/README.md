# LifeSchool Frontend

**Radhe Radhe! 🙏**

Frontend application for the LifeSchool exam registration platform.

## Tech Stack

- **React 18**
- **Vite** (build tool)
- **React Router** (routing)
- **Axios** (HTTP client)

## Setup

### Prerequisites

- Node.js 18+ and npm/yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Features

- **Login Page**: Mock Google SSO login
- **Profile Page**: View and update user profile
- **Mobile Number Update**: Complete profile by adding 10-digit mobile number
- **Protected Routes**: Authentication-required routes
- **Responsive Design**: Modern, clean UI

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   │   └── ProtectedRoute.jsx
│   ├── contexts/         # React contexts
│   │   └── AuthContext.jsx
│   ├── pages/           # Page components
│   │   ├── Login.jsx
│   │   └── Profile.jsx
│   ├── services/        # API services
│   │   └── api.js
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── vite.config.js
└── package.json
```

## API Integration

The frontend communicates with the backend API through a proxy configured in `vite.config.js`. All API calls are prefixed with `/api` which gets proxied to `http://localhost:8000`.

## Environment Variables

Create a `.env` file if needed:

```env
VITE_API_URL=http://localhost:8000
```

## Notes

- Google SSO is currently mocked (no real Google API integration)
- Authentication tokens are stored in localStorage
- Mobile number validation: exactly 10 digits

