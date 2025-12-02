# Task Management Frontend

A modern React TypeScript frontend for the Task Management & Collaboration application.

## Features

- **Authentication**: User registration and JWT-based login
- **Project Management**: Create, view, and manage projects
- **Task Tracking**: Create tasks, assign them, and track progress through different statuses (To Do, In Progress, Done)
- **Team Collaboration**: Manage project members and their roles
- **Responsive Design**: Mobile-friendly interface with TailwindCSS

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Client-side routing
- **TailwindCSS** - Styling
- **Fetch API** - API communication

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure the API URL in `.env`:
```
VITE_API_URL=http://127.0.0.1:8000
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://127.0.0.1:5173`

## Build

```bash
npm run build
```

## Project Structure

```
src/
├── api/
│   └── client.ts          # API client for backend communication
├── context/
│   ├── AuthContext.tsx    # Authentication state management
│   └── ProjectContext.tsx # Project state management
├── pages/
│   ├── LoginPage.tsx      # Login page
│   ├── RegisterPage.tsx   # Registration page
│   ├── DashboardPage.tsx  # Main dashboard with projects
│   └── ProjectDetailPage.tsx # Project details and task management
├── components/
│   └── ProtectedRoute.tsx # Protected route wrapper
├── App.tsx                # Main app component with routing
└── main.tsx               # Entry point
```

## API Endpoints Used

### Authentication
- `POST /users/register` - Register new user
- `POST /users/login` - Login user
- `POST /users/me` - Get current user info

### Projects
- `POST /projects/` - Create project
- `GET /projects/` - List projects
- `GET /projects/{project_id}` - Get project details
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project

### Tasks
- `POST /projects/{project_id}/tasks/` - Create task
- `GET /projects/{project_id}/tasks/` - List project tasks
- `PUT /projects/{project_id}/tasks/{task_id}` - Update task
- `DELETE /projects/{project_id}/tasks/{task_id}` - Delete task

## Authentication

The app uses JWT tokens for authentication. Tokens are stored in localStorage and automatically attached to all API requests.

## License

MIT

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
