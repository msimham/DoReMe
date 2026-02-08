"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, MessageCircle, Search, User, Settings, LogOut, Menu, X } from "lucide-react";
import { useState } from "react";

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/dm", label: "DM", icon: MessageCircle },
  { href: "/find", label: "Find & Search", icon: Search },
  { href: "/profile", label: "Profile", icon: User },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden w-10 h-10 bg-white border border-black/10 rounded-lg flex items-center justify-center shadow-lg"
      >
        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 bg-black/50 z-40 lg:hidden animate-fade-in"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`w-64 h-screen bg-white border-r border-black/10 flex flex-col fixed left-0 top-0 z-50 transition-transform duration-300 lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-black/10">
          <Link href="/" onClick={() => setMobileOpen(false)}>
            <h1 className="text-3xl font-bold tracking-tight">DoReMe</h1>
            <p className="text-xs text-black/40 mt-1 tracking-wide">@yourhandle</p>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={isActive ? "nav-item-active" : "nav-item"}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Bottom actions */}
        <div className="p-4 border-t border-black/10 space-y-1">
          <button className="nav-item w-full">
            <Settings size={20} />
            <span>Settings</span>
          </button>
          <button className="nav-item w-full">
            <LogOut size={20} />
            <span>Log Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
