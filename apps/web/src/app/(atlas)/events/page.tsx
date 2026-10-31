import { Metadata } from 'next';
import { UniversalEventExplorer } from '@/components/events/UniversalEventExplorer';

export const metadata: Metadata = {
  title: 'Universal Events | ATLAS',
  description:
    'Canonical Financial, Economic, Corporate, Regulatory, Sanctions, Geopolitical and Physical-World Events Intelligence Foundation.',
};

export default function EventsPage() {
  return (
    <div className="h-full flex flex-col overflow-hidden bg-black">
      <UniversalEventExplorer />
    </div>
  );
}
