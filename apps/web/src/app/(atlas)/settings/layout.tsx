import React from 'react';
import { SettingsSidebar } from '@/components/settings/SettingsSidebar';
import { getSettingsCategory } from '@/config/settings-registry';

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-1 h-full w-full bg-atlas-bg-0 text-atlas-text-primary overflow-hidden">
      <SettingsSidebar />
      <div className="flex-1 overflow-y-auto custom-scrollbar flex justify-center p-6 lg:p-12">
        <div className="w-full max-w-[1000px] flex flex-col pb-20">
          {children}
        </div>
      </div>
    </div>
  );
}
