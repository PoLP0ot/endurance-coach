import { SiteHeader } from "@/components/marketing/site-header";
import { Pricing } from "@/components/marketing/pricing";
import { SiteFooter } from "@/components/marketing/site-footer";

export const metadata = {
  title: "Pricing — Endurance Coach",
  description: "Simple pricing — free forever, or go Premium for the full AI coach.",
};

export default function PricingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="flex-1">
        <Pricing />
      </main>
      <SiteFooter />
    </div>
  );
}
