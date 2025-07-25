# ClosetGPT

ClosetGPT is an AI-powered personal stylist application that helps users manage their wardrobe, get outfit recommendations, and receive personalized style advice.

## Features

- **AI Outfit Recommendations**: Get personalized outfit suggestions based on your style preferences and occasion
- **Wardrobe Management**: Organize and track your clothing items, accessories, and shoes
- **Style Advice**: Receive expert fashion advice tailored to your personal style
- **Modern UI**: Beautiful and responsive user interface built with Next.js and Tailwind CSS

## Tech Stack

- **Frontend**:
  - Next.js 14
  - React
  - TypeScript
  - Tailwind CSS
  - shadcn/ui Components
  - Radix UI Primitives

## Development Setup

### Requirements
- Python 3.11 (required for backend)
- Node.js (for frontend)

### Port Configuration
- Frontend: http://localhost:3000
- Backend: http://localhost:3001

### Getting Started

1. Backend Setup:
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

2. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:3001

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js app directory
│   │   ├── dashboard/      # Dashboard page
│   │   ├── login/         # Login page
│   │   ├── signup/        # Signup page
│   │   └── layout.tsx     # Root layout
│   ├── components/         # React components
│   │   ├── ui/            # UI components
│   │   └── Navigation.tsx # Navigation component
│   └── lib/               # Utility functions
└── public/                # Static assets
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 