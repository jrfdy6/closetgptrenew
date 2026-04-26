# Easy Outfit App Frontend

This is the Next.js frontend for Easy Outfit App.

## Local Setup

1. Install dependencies:
```bash
npm ci
```

2. Create a local env file:
```bash
cp env.example .env.local
```

3. Update `.env.local`:
- Set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_BACKEND_URL` to your backend base URL.
- Fill in the `NEXT_PUBLIC_FIREBASE_*` values for the Firebase project.
- Leave `ENABLE_INTERNAL_DEBUG_PAGES=false` unless you intentionally need internal debug or demo routes exposed.

4. Start the app:
```bash
npm run dev
```

The frontend runs on `http://localhost:3000`.

## Build

```bash
npm run build
```

## Notes

- Production deploys are expected to run on Vercel.
- Internal routes such as `/personalization-demo`, `/debug-*`, `/test*`, and related debug APIs are blocked in production unless `ENABLE_INTERNAL_DEBUG_PAGES=true` is set.
