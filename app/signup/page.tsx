"use client";

import Link from "next/link";
import { useForm } from "react-hook-form";
import InputRow from "../_components/InputRow";
import { signUpAction } from "../_lib/actions";
import { SignUpFormValues } from "../_types/types";
import InputErrorMessage from "../_components/InputErrorMessage";
import { useState } from "react";
import Button from "../_components/Button";

function Page() {
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SignUpFormValues>();

  async function onSubmit(data: SignUpFormValues) {
    try {
      await signUpAction(data);
    } catch (err) {
      if (err instanceof Error) setError("This feature is disabled.");
    }
  }

  return (
    <div className="mt-8 flex flex-col items-center gap-4 md:mt-32 md:gap-8">
      <div className="flex flex-col gap-6 rounded-md dark:border-gray-700 sm:p-16 md:border md:bg-gray-100 md:dark:bg-gray-900/90">
        <h2 className="text-3xl font-bold text-gray-700 dark:text-gray-300 sm:text-4xl">
          Create new account
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
              Email
            </label>
            <input
              type="email"
              className="text-md h-10 w-80 rounded-md border-2 border-transparent p-2 text-center text-gray-800 shadow-sm outline-none transition-all duration-200 focus:border-red-700 focus:shadow-lg dark:bg-gray-700 dark:text-gray-200"
              placeholder="jankowalski@mail.com"
              {...register("email", { required: "Email is required." })}
            />
            {errors.email && (
              <InputErrorMessage>{errors.email.message}</InputErrorMessage>
            )}
          </InputRow>
          <InputRow>
            <label
              htmlFor="firstName"
              className="text-md font-semibold text-gray-500"
            >
              First name
            </label>
            <input
              type="text"
              className="text-md h-10 w-80 rounded-md border-2 border-transparent p-2 text-center text-gray-800 shadow-sm outline-none transition-all duration-200 focus:border-red-700 focus:shadow-lg dark:bg-gray-700 dark:text-gray-200"
              placeholder="John"
              {...register("firstName", {
                required: "First name is required.",
                minLength: {
                  value: 3,
                  message: "First name should be at least 3 characters.",
                },
              })}
            />
            {errors.firstName && (
              <InputErrorMessage>{errors.firstName.message}</InputErrorMessage>
            )}
          </InputRow>
          <InputRow>
            <label
              htmlFor="lastName"
              className="text-md font-semibold text-gray-500"
            >
              Last name
            </label>
            <input
              type="text"
              className="text-md h-10 w-80 rounded-md border-2 border-transparent p-2 text-center text-gray-800 shadow-sm outline-none transition-all duration-200 focus:border-red-700 focus:shadow-lg dark:bg-gray-700 dark:text-gray-200"
              placeholder="Kowalski"
              {...register("lastName", {
                required: "Last name is required.",
                minLength: {
                  value: 3,
                  message: "Last name should be at least 3 characters.",
                },
              })}
            />
            {errors.lastName && (
              <InputErrorMessage>{errors.lastName.message}</InputErrorMessage>
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
              {...register("password", {
                required: "Password is required",
                minLength: {
                  value: 8,
                  message: "Password must be at least 8 characters.",
                },
              })}
            />
            {errors.password && (
              <InputErrorMessage>{errors.password.message}</InputErrorMessage>
            )}
          </InputRow>
          <InputRow>
            <label
              htmlFor="confirmpassword"
              className="text-md font-semibold text-gray-500"
            >
              Confirm password
            </label>
            <input
              type="password"
              className="text-md h-10 w-80 rounded-md border-2 border-transparent p-2 text-center text-gray-800 shadow-sm outline-none transition-all duration-200 focus:border-red-700 focus:shadow-lg dark:bg-gray-700 dark:text-gray-200"
              {...register("confirmPassword", {
                required: "Please confirm your password.",
                validate: (val) =>
                  val === watch("password") || "Passwords have to be the same.",
              })}
            />
            {errors.confirmPassword && (
              <InputErrorMessage>
                {errors.confirmPassword.message}
              </InputErrorMessage>
            )}
          </InputRow>
          <div className="flex w-full items-center justify-between">
            <Link
              href="/login"
              className="underline-offset-3 border-gray-500 text-sm font-semibold text-gray-500 hover:underline"
            >
              I already have an account
            </Link>
            <div>
              <Button type="primary">Sign Up</Button>
            </div>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </form>
      </div>
    </div>
  );
}

export default Page;
