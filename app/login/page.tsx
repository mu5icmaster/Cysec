"use client";

import Link from "next/link";
import { redirect } from "next/navigation";
import { useForm } from "react-hook-form";
import InputRow from "../_components/InputRow";
import { useState, useTransition } from "react";
import Button from "../_components/Button";
import { loginAction } from "../_lib/actions";

interface LoginData {
  email: string;
  password: string;
}

function Page() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginData>({
    defaultValues: { email: "test@test.com", password: "test1234" }, // default values set for users to test app
  });
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState("");

  async function onSubmit(data: LoginData) {
    try {
      const { email, password } = data;
      startTransition(async () => {
        await loginAction({ email, password });
        redirect("/account");
      });
    } catch (err) {
      if (err instanceof Error) {
        setError("Username or password is incorrect.");
      }
    }
  }

  return (
    <div className="mt-8 flex flex-col items-center gap-8 md:mt-32">
      <div className="flex h-96 w-96 flex-col items-center justify-center gap-4 rounded-md p-8 dark:border-gray-700 md:border md:bg-gray-100 md:dark:bg-gray-900/90">
        <h2 className="text-center text-3xl font-bold text-gray-700 dark:text-gray-300 sm:text-4xl">
          Login
        </h2>
        <form
          className="flex flex-col items-center gap-2"
          onSubmit={handleSubmit(onSubmit)}
        >
          <InputRow>
            <label
              htmlFor="email"
              className="text-md font-semibold text-gray-500"
            >
              Login
            </label>
            <input
              type="email"
              className="text-md h-10 w-80 rounded-md border-2 border-transparent p-2 text-center text-gray-800 shadow-sm outline-none transition-all duration-200 focus:border-red-700 focus:shadow-lg dark:bg-gray-700 dark:text-gray-200"
              placeholder="jankowalski@mail.com"
              {...register("email", { required: "Email is required." })}
            />
            {errors.email && (
              <span className="text-sm text-red-600">
                {errors.email.message}
              </span>
            )}
          </InputRow>
          <InputRow>
            <label
              htmlFor="password"
              className="text-md font-semibold text-gray-500"
            >
              Password
            </label>
            <input
              type="password"
              className="text-md h-10 w-80 rounded-md border-2 border-transparent p-2 text-center text-gray-800 shadow-sm outline-none transition-all duration-200 focus:border-red-700 focus:shadow-lg dark:bg-gray-700 dark:text-gray-200"
              {...register("password", { required: "Password is required." })}
            />
            {errors.password && (
              <span className="text-sm text-red-600">
                {errors.password.message}
              </span>
            )}
          </InputRow>
          {error && <span className="text-sm text-red-600">{error}</span>}
          <div className="flex w-full items-center justify-between">
            <Link
              href="/signup"
              className="underline-offset-3 border-gray-500 text-sm font-semibold text-gray-500 hover:underline"
            >
              I don&apos;t have an account yet
            </Link>
            <Button type="primary" disabled={isPending}>
              Login
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Page;
