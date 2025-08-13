"use client";
import { supabase } from "@/lib/supabase";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { useForm } from "react-hook-form";

const page = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const submitSignUpDetails = async (formDetails) => {
    setIsLoading(true);
    setError("");
    setSuccess(false);

    const { email, displayName, password } = formDetails;

    try {
      const { error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            display_name: displayName,
          },
        },
      });

      if (signUpError) {
        throw new Error(signUpError.message);
      }

      setSuccess(true);
      console.log("Signup successful!");
      router.push("/login");
    } catch (err) {
      setError(err.message || "An unexpected error occurred during signup.");
      console.error("Signup failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-gray-900 font-inter">
      <div className="relative w-full max-w-md mx-auto">
        {error && <p className="text-red-400 text-sm mt-1">{error}</p>}
        <form
          onSubmit={handleSubmit(submitSignUpDetails)}
          className="relative z-10 p-8 shadow-lg bg-white/10 backdrop-blur-md border rounded-3xl border-white/20 grid gap-6 transition-all duration-300 ease-in-out hover:shadow-3xl"
        >
          <h2 className="text-4xl font-extrabold text-white text-center mb-4 tracking-tight">
            Welcome
          </h2>

          <div>
            <label
              htmlFor="email"
              className="block text-lg font-medium text-gray-200 mb-2"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              placeholder="you@example.com"
              className="w-full px-5 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              {...register("email", {
                required: "Email is required",
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: "Invalid email address",
                },
              })}
            />
            {errors.email && (
              <p className="text-red-400 text-sm mt-1">
                {errors.email.message}
              </p>
            )}
          </div>
          <div>
            <label
              htmlFor="displayName"
              className="block text-lg font-medium text-gray-200 mb-2"
            >
              Display Name
            </label>
            <input
              type="text"
              id="displayName"
              placeholder="Caleb"
              className="w-full px-5 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              {...register("displayName", {
                required: "Display Name is required",
              })}
            />
            {errors.displayName && (
              <p className="text-red-400 text-sm mt-1">
                {errors.displayName.message}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-lg font-medium text-gray-200 mb-2"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              placeholder="Enter your password"
              className="w-full px-5 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              {...register("password", {
                required: "Password is required",
                minLength: {
                  value: 6,
                  message: "Password must be at least 6 characters",
                },
              })}
            />
            {errors.password && (
              <p className="text-red-400 text-sm mt-1">
                {errors.password.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            className="cursor-pointer w-full px-6 py-3 mt-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-lg rounded-lg shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75"
          >
            Submit
          </button>
        </form>

        <p className="text-gray-300 text-center mt-8 text-lg">
          Already have an account?{" "}
          <Link
            href="/login"
            className="text-blue-400 font-semibold hover:text-blue-300 transition-colors duration-200"
          >
            Login
          </Link>
        </p>
      </div>
    </section>
  );
};

export default page;
