# DoReMe - Quick Start Guide

## Instant Setup (3 steps)

1. **Install dependencies**
   ```bash
   cd doreme
   npm install
   ```

2. **Run the app**
   ```bash
   npm run dev
   ```

3. **Open browser**
   ```
   http://localhost:3000
   ```

That's it! The app will run with mock data by default.

## What You'll See

- **Home Feed** (`/`): Browse video content from musicians
- **DMs** (`/dm`): Send messages to other musicians
- **Find** (`/find`): Swipe through musician profiles (like Tinder)
- **Profile** (`/profile`): Manage your projects and drafts

## Key Features Working Out of the Box

✅ Persistent storage (localStorage)
✅ Mock data included
✅ Mobile responsive
✅ Keyboard shortcuts (← and → on Find page)
✅ Real-time typing indicators in DMs
✅ Video embeds (YouTube)
✅ Project management with video/notes/lyrics

## Optional: Add Real Video Search

Get a free API key from [SerpAPI](https://serpapi.com/) (100 searches/month free)

Create `.env.local`:
```
NEXT_PUBLIC_SERPAPI_KEY=your_key_here
```

Restart the dev server and the Home Feed will fetch real YouTube results!

## Customization

All mock data is in `lib/mockData.ts` - edit to add your own:
- Musicians
- Videos
- Conversations

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- Lucide React (icons)
- localStorage (persistence)

## Need Help?

Check the main README.md for full documentation.

Enjoy building with DoReMe! 🎵
