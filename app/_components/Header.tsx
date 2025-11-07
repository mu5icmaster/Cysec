"use client";

import Link from "next/link";
import {
  IoCartOutline,
  IoClose,
  IoMenuOutline,
  IoPersonOutline,
} from "react-icons/io5";
import { useCart } from "./CartContext";
import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import ToggleDarkMode from "./ToggleDarkMode";
import { Badge } from "./Badge";

function Header() {
  const pathname = usePathname();
  const { cart } = useCart();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const overlay = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const overlayEl = overlay?.current;
    function handleCloseMenu() {
      setIsMenuOpen(false);
    }
    if (overlayEl) {
      overlayEl.addEventListener("click", handleCloseMenu);
      return () => overlayEl.removeEventListener("click", handleCloseMenu);
    }
  }, [isMenuOpen]);

  return (
    <>
      <header className="fixed z-50 flex h-[70px] w-full items-center gap-4 bg-gray-100/90 px-6 font-semibold text-gray-700 shadow-sm backdrop-blur-lg dark:bg-gray-900/90 dark:text-gray-300 sm:gap-10 sm:px-12">
        <div className="z-10 lg:w-64">
          <Link
            className="text-2xl font-semibold tracking-tight text-gray-700 transition-all duration-200 dark:text-gray-300"
            href="/"
          >
            hardwar<span className="text-red-700 dark:text-red-600">i</span>fy
          </Link>
        </div>
        <button
          onClick={() => setIsMenuOpen(true)}
          className="transition-color z-10 block text-3xl duration-150 hover:text-gray-500 dark:hover:text-gray-300/90 lg:hidden"
        >
          <IoMenuOutline />
        </button>
        <nav className="z-10 w-full">
          <ul className="flex items-center gap-8 text-lg duration-300">
            <div className="flex w-full justify-center gap-12">
              <li className="hidden transition-colors hover:text-gray-600 dark:hover:text-gray-300/90 lg:block">
                <Link
                  href="/"
                  className={`${pathname === "/" ? "after:scale-x-100" : ""} relative block after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-700 after:transition after:duration-300 after:content-[''] after:hover:scale-x-100 dark:after:bg-gray-300`}
                >
                  Home
                </Link>
              </li>
              <li className="hidden transition-colors hover:text-gray-600 dark:hover:text-gray-300/90 lg:block">
                <Link
                  href="/products"
                  className={`${pathname.startsWith("/products") ? "after:scale-x-100" : ""} relative block after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-700 after:transition after:duration-300 after:content-[''] after:hover:scale-x-100 dark:after:bg-gray-300`}
                >
                  Products
                </Link>
              </li>
              <li className="hidden transition-colors hover:text-gray-600 dark:hover:text-gray-300/90 lg:block">
                <Link
                  href="/about"
                  className={`${pathname === "/about" ? "after:scale-x-100" : ""} relative block after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-700 after:transition after:duration-300 after:content-[''] after:hover:scale-x-100 dark:after:bg-gray-300`}
                >
                  About
                </Link>
              </li>
            </div>
            <div className="flex items-center gap-4 lg:w-64 lg:gap-8">
              <li className="ml-auto hidden transition-colors hover:text-gray-600 dark:hover:text-gray-300/90 lg:block">
                <ToggleDarkMode />
              </li>
              <li className="transition-colors hover:text-gray-600 dark:hover:text-gray-300/90">
                <div className="relative">
                  <Badge
                    className={`absolute -right-2 -top-2 h-5 min-w-5 scale-0 rounded-full bg-red-600 dark:bg-red-700 ${cart.length > 0 ? "scale-100" : "scale-0"}`}
                  >
                    {cart.length}
                  </Badge>
                  <Link href="/cart" className="text-4xl">
                    <IoCartOutline />
                  </Link>
                </div>
              </li>
              <li className="hidden transition-colors hover:text-gray-600 dark:hover:text-gray-300/90 lg:block">
                <Link href="/account" className="text-3xl">
                  <IoPersonOutline />
                </Link>
              </li>
            </div>
          </ul>
        </nav>

        {/* MOBILE */}
        <nav
          className={`absolute left-0 top-0 h-screen w-3/4 ${isMenuOpen ? "translate-x-0" : "-translate-x-[150%]"} z-50 transform bg-gray-50 shadow-md transition-transform dark:bg-gray-900 md:w-1/2 lg:hidden`}
        >
          <div className="absolute left-0 flex h-[70px] w-full items-center justify-between px-8">
            <ToggleDarkMode />
            <button
              onClick={() => setIsMenuOpen(false)}
              className="flex items-center justify-center text-3xl text-gray-700 dark:text-gray-300"
            >
              <IoClose />
            </button>
          </div>
          <div className="flex h-full w-full items-center justify-center">
            <ul className="flex w-full flex-col gap-12 py-2 text-gray-700 dark:border-gray-700 dark:text-gray-300">
              <li className="flex w-full justify-center text-2xl transition-colors duration-100 hover:text-gray-500 dark:hover:text-gray-300">
                <Link
                  className={`${pathname === "/" ? "after:scale-x-100" : ""} relative block after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-700 after:transition after:duration-300 after:content-[''] dark:after:bg-gray-300`}
                  href="/"
                >
                  Home
                </Link>
              </li>
              <li className="flex w-full justify-center text-2xl transition-colors duration-100 hover:text-gray-500 dark:border-gray-800 dark:hover:text-gray-300">
                <Link
                  className={`${pathname.startsWith("/products") ? "after:scale-x-100" : ""} relative block after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-700 after:transition after:duration-300 after:content-[''] dark:after:bg-gray-300`}
                  href="/products"
                >
                  Products
                </Link>
              </li>
              <li className="flex w-full justify-center text-2xl transition-colors duration-100 hover:text-gray-500 dark:border-gray-800 dark:hover:text-gray-300">
                <Link
                  className={`${pathname.startsWith("/about") ? "after:scale-x-100" : ""} relative block after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-700 after:transition after:duration-300 after:content-[''] dark:after:bg-gray-300`}
                  href="/about"
                >
                  About
                </Link>
              </li>
              <li className="flex w-full justify-center text-2xl transition-colors duration-100 hover:text-gray-500 dark:border-gray-800 dark:hover:text-gray-300">
                <Link
                  className={`${pathname.startsWith("/account") || pathname.startsWith("/login") || pathname.startsWith("/signup") ? "after:scale-x-100" : ""} relative block after:absolute after:block after:h-[2px] after:w-full after:origin-center after:scale-x-0 after:bg-gray-700 after:transition after:duration-300 after:content-[''] dark:after:bg-gray-300`}
                  href="/account"
                >
                  Account
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      </header>
      {isMenuOpen && (
        <div
          ref={overlay}
          className="fixed z-[4] h-screen max-h-full w-screen max-w-full backdrop-blur-[2px] lg:hidden"
        ></div>
      )}
    </>
  );
}
export default Header;
