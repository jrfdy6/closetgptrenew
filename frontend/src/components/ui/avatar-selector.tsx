import { cn } from '@/lib/utils';

interface AvatarSelectorProps {
  selectedUrl: string | null;
  onSelect: (url: string) => void;
}

const AVATAR_OPTIONS = [
  {
    id: 'avatar1',
    url: '/avatars/avatar1.png',
    label: 'Avatar 1',
  },
  {
    id: 'avatar2',
    url: '/avatars/avatar2.png',
    label: 'Avatar 2',
  },
  {
    id: 'avatar3',
    url: '/avatars/avatar3.png',
    label: 'Avatar 3',
  },
  {
    id: 'avatar4',
    url: '/avatars/avatar4.png',
    label: 'Avatar 4',
  },
];

export function AvatarSelector({ selectedUrl, onSelect }: AvatarSelectorProps) {
  return (
    <div className="grid grid-cols-4 gap-4">
      {AVATAR_OPTIONS.map((avatar) => (
        <button
          key={avatar.id}
          onClick={() => onSelect(avatar.url)}
          className={cn(
            'aspect-square rounded-lg overflow-hidden border-2 transition-all',
            selectedUrl === avatar.url
              ? 'border-primary ring-2 ring-primary ring-offset-2'
              : 'border-transparent hover:border-gray-200'
          )}
        >
          <img
            src={avatar.url}
            alt={avatar.label}
            className="w-full h-full object-cover"
          />
        </button>
      ))}
    </div>
  );
} 