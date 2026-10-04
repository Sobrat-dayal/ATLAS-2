import { notFound } from "next/navigation";
import { getSettingsCategory } from "@/config/settings-registry";
import { SettingsPage } from "@/components/settings/SettingsControls";
import { GeneralSettings } from "@/components/settings/categories/GeneralSettings";
import { AppearanceSettings } from "@/components/settings/categories/AppearanceSettings";
import { KeyboardSettings } from "@/components/settings/categories/KeyboardSettings";
import { StorageSettings } from "@/components/settings/categories/StorageSettings";
import { AccessibilitySettings } from "@/components/settings/categories/AccessibilitySettings";
import { DeveloperSettings } from "@/components/settings/categories/DeveloperSettings";
import { AdvancedSettings } from "@/components/settings/categories/AdvancedSettings";
import { FoundationSettings } from "@/components/settings/categories/FoundationSettings";

export default function SettingsCategoryPage({
  params,
}: {
  params: { category: string };
}) {
  const category = getSettingsCategory(params.category);

  if (!category) {
    notFound();
  }

  const renderContent = () => {
    switch (category.id) {
      case "general":
        return <GeneralSettings />;
      case "appearance":
        return <AppearanceSettings />;
      case "keyboard":
        return <KeyboardSettings />;
      case "storage":
        return <StorageSettings />;
      case "accessibility":
        return <AccessibilitySettings />;
      case "developer":
        return <DeveloperSettings />;
      case "advanced":
        return <AdvancedSettings />;
      default:
        // Render foundation state for unavailable categories
        return <FoundationSettings category={category} />;
    }
  };

  return (
    <SettingsPage category={category}>
      {renderContent()}
    </SettingsPage>
  );
}
