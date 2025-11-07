"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import SignOutButton from "./SignOutButton";

const links = [
  {
    name: "General",
    href: "/account",
  },
  {
    name: "My orders",
    href: "/account/orders",
  },
  {
    name: "Previous orders",
    href: "/account/pastorders",
  },
  {
    name: "Settings",
    href: "/account/settings",
  },
];

function AccountMenu() {
  const pathname = usePathname();

  return (
    <div className="border-y-2 md:border-y-0 md:border-r-2 dark:border-gray-600">
      <nav className="md:p-4">
        <ul className="flex-col gap-4 text-xl text-gray-700 lg:flex dark:text-gray-300">
          {links.map((link) => (
            <li className={`mt-2 rounded-lg lg:mt-0`} key={link.href}>
              <Link
                href={link.href}
                className={`block h-full rounded-lg p-2 text-center hover:bg-gray-200 md:text-left dark:hover:bg-gray-800 ${link.href === pathname ? "bg-gray-200 font-semibold dark:bg-gray-800" : ""}`}
              >
                {link.name}
              </Link>
            </li>
          ))}
          <SignOutButton />
        </ul>
      </nav>
    </div>
  );
}

export default AccountMenu;
