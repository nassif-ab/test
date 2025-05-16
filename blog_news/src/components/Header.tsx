import AuthModal from "./AuthModal"
import { useState } from "react";
import { useAuth } from "../content/AuthProvider";
import { Link } from "react-router-dom";

const mainMenuItems = [
    { label: "L'UNIVERSITÉ", href: "/" },
    { label: "VISITE", href: "/visite" },
    { label: "AGENDA", href: "/agenda" },
    { label: "CONTACT", href: "/contact" },
];
const secondaryMenuItems = [
    { label: "Accueil", href: "/" },
    { label: "ENSAS", href: "/ensas" },
    { label: "FORMATIONS", href: "/formations" },
    { label: "ESPACE ÉTUDIANT", href: "/espace-etudiant" },
    { label: "RECHERCHE", href: "/recherche" },
    { label: "COOPÉRATION", href: "/cooperation" },
    { label: "ACTIVITÉS PARASCOLAIRES", href: "/activites-parascolaires" },
];

const Header = () => {
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
    const { user, logout, isAuthenticated } = useAuth();

    const handleLogout = () => {
        logout();
    };

    return (
        <header className="w-full">
{/* نافذة تسجيل الدخول/إنشاء حساب */}
<AuthModal
  isOpen={isAuthModalOpen} 
  onClose={() => setIsAuthModalOpen(false)}
/>
<div className="flex container mx-auto items-center px-4 py-2 border-b bg-white">
  {/* Logo + School name */}
  <div className="flex items-center gap-3 flex-1">
    <img
      src="/logo.png"
      alt="Logo"
      className="h-12"
    />
{/*           <div className="hidden md:block">
      <div className="font-bold text-[#063267] leading-tight text-lg">
        المدرسة الوطنية للعلوم التطبيقية – القنيطرة
      </div>
      <div className="text-blue-800 text-sm">
        National School of Applied Sciences – Kenitra
      </div>
    </div> */}
  </div>
  {/* Top menu */}
  <nav className="hidden md:flex gap-6 text-sm font-medium text-gray-700 uppercase">
    
    {mainMenuItems.map((item) => (
      <Link key={item.label} to={item.href} className="hover:underline">
        {item.label}
      </Link>
    ))}
    {user ? (
      <div className="flex items-center gap-3">
        <span className="text-[#063267]">
          bienvenue {user.fullName}
        </span>
        <button 
          onClick={handleLogout}
          className="bg-[#063267] text-white px-3 py-1 rounded-md text-xs hover:bg-[#052a56] transition-colors"
        >
          Déconnexion
        </button>
      </div>
    ) : (
      <button 
        onClick={() => setIsAuthModalOpen(true)}
        className="bg-[#063267] text-white px-3 py-1 rounded-md text-xs hover:bg-[#052a56] transition-colors"
      >
        Se connecter / S'inscrire
      </button>
    )}
  </nav>
</div>
{/* Main Nav */}
<div className="bg-[#063267] text-white text-sm font-semibold px-2 py-2">
  <nav className="flex flex-wrap gap-x-8 gap-y-2 justify-center max-w-6xl mx-auto">
    {secondaryMenuItems.map((item) => (
      <Link key={item.label} to={item.href} className="hover:underline">
        {item.label}
      </Link>
    ))}

  </nav>
</div>
</header>
    )
}

export default Header;
