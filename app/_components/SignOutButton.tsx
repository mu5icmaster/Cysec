"use client";
import { IoLogOutOutline } from "react-icons/io5";
import { signOutAction } from "../_lib/actions";
import { FormEvent } from "react";

function SignOutButton() {
  async function handleSignOut(e: FormEvent) {
    e.preventDefault();
    await signOutAction();
  }

  return (
    <form onSubmit={handleSignOut}>
      <button className="flex w-full items-center justify-center gap-2 rounded-lg p-2 text-center text-red-600 hover:bg-gray-200 md:justify-start md:text-left dark:hover:bg-gray-700">
        <IoLogOutOutline />
        <span>Sign out</span>
      </button>
    </form>
  );
}

export default SignOutButton;
