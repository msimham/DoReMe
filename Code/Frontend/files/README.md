# DoReMe - Musician Collaboration Platform

A minimal, clean front-end application for musicians to discover, connect, and collaborate. Built with Next.js, TypeScript, and TailwindCSS.

## Features

- **Home Feed**: Browse video content from musicians (YouTube integration via SerpAPI or mock data)
- **Direct Messages**: Slack-style DM interface with real-time typing indicators
- **Smart Matching**: Tinder/Hinge-style musician discovery with filters
- **Profile & Projects**: Manage public projects and private drafts with video/notes/lyrics
- **Persistent Storage**: All data persists in localStorage (no backend required)

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Icons**: Lucide React
- **Storage**: localStorage
- **API**: SerpAPI (optional, graceful fallback to mock data)

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

1. Clone or extract the project files

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

3. (Optional) Add SerpAPI key for real video search:
Create a `.env.local` file in the root:
```
NEXT_PUBLIC_SERPAPI_KEY=your_serpapi_key_here
```

If you don't provide an API key, the app will use mock data automatically.

### Running the Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
doreme/
├── app/
│   ├── layout.tsx          # Root layout with sidebar
│   ├── page.tsx            # Home feed page
│   ├── dm/page.tsx         # DM page
│   ├── find/page.tsx       # Smart matching page
│   ├── profile/page.tsx    # Profile & projects page
│   └── globals.css         # Global styles
├── components/
│   ├── Sidebar.tsx         # Navigation sidebar
│   ├── FeedCard.tsx        # Video feed card
│   ├── MatchCard.tsx       # Musician match card
│   ├── DMThread.tsx        # DM conversation thread
│   ├── ProfileProjectCard.tsx  # Project card
│   └── LoadingSkeleton.tsx # Loading state
├── lib/
│   ├── types.ts            # TypeScript types
│   ├── mockData.ts         # Mock data for development
│   ├── storage.ts          # localStorage helpers
│   └── serpApiClient.ts    # SerpAPI integration
└── package.json
```

## Usage Guide

### Home Feed (/)
- Search for videos by artist, song, or genre
- Like, comment, and share videos
- Browse content from other musicians

### DMs (/dm)
- View all conversations in the left sidebar
- Click to open a conversation
- Send messages with real-time simulation
- Start new conversations with the + button

### Find & Search (/find)
- Swipe through musician profiles (Tinder-style)
- Filter by abilities, looking-for, and location
- Use keyboard shortcuts: ← to pass, → to like
- Match with musicians to start collaborating

### Profile (/profile)
- View and edit your profile information
- Manage public projects (visible to others)
- Work on private drafts (only you can see)
- Upload videos, add notes and lyrics
- Track project stage (Idea, Demo, Draft, Polished)

## Data Persistence

All data is stored in localStorage:
- **Conversations**: DM threads and messages
- **Projects**: Your music projects (public and private)
- **Matches**: Liked and passed musicians

To reset all data, clear your browser's localStorage.

## Customization

### Styling
Edit `app/globals.css` to customize colors, typography, and spacing.

### Mock Data
Edit `lib/mockData.ts` to add more musicians, videos, or conversations.

### Components
All components in `/components` are standalone and can be easily customized.

## Keyboard Shortcuts

- **Find page**: Left arrow (pass), Right arrow (like)
- **DM page**: Enter to send message

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Known Limitations

- Front-end only (no real backend)
- No user authentication
- No real video uploads (uses object URLs for preview only)
- localStorage limited to ~5-10MB
- No real-time collaboration features

## Future Enhancements

Potential features to add:
- Dark mode toggle
- Onboarding modal for new users
- Toast notifications
- Export projects to JSON
- Audio player for music files
- Calendar integration for sessions
- Real-time collaboration (requires backend)

## License

MIT

## Credits

Built with ❤️ for musicians worldwide.
