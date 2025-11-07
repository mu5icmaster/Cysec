"use client";

import { useTheme } from "next-themes";
import { MdOutlineDarkMode, MdOutlineLightMode } from "react-icons/md";

function ToggleDarkMode() {
  const { setTheme, theme } = useTheme();

  return (
    <>
      <button
        onClick={() => {
          if (theme === "dark") setTheme("light");
          if (theme === "light") setTheme("dark");
        }}
        className="flex items-center justify-center rounded-full text-3xl dark:hidden"
      >
        <MdOutlineDarkMode className="scale-100 dark:scale-0" />
      </button>
      <button
        onClick={() => {
          if (theme === "dark") setTheme("light");
          if (theme === "light") setTheme("dark");
        }}
        className="hidden items-center justify-center rounded-full text-3xl dark:flex"
      >
        <MdOutlineLightMode />
      </button>
    </>
  );
}

export default ToggleDarkMode;
