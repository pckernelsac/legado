import { PatternBackground } from "@/components/brand/PatternBackground";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { HeroSection } from "@/pages/landing/sections/HeroSection";
import { HowItWorksSection } from "@/pages/landing/sections/HowItWorksSection";
import { BenefitsSection } from "@/pages/landing/sections/BenefitsSection";
import { StoriesSection } from "@/pages/landing/sections/StoriesSection";
import { PlansSection } from "@/pages/landing/sections/PlansSection";
import { FaqSection } from "@/pages/landing/sections/FaqSection";
import { ContactSection } from "@/pages/landing/sections/ContactSection";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      <PatternBackground intensity={2.6} />
      <div className="relative z-10">
        <Navbar />
        <main>
          <HeroSection />
          <HowItWorksSection />
          <BenefitsSection />
          <StoriesSection />
          <PlansSection />
          <FaqSection />
          <ContactSection />
        </main>
        <Footer />
      </div>
    </div>
  );
}
