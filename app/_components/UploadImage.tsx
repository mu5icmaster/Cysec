"use client";

import { useForm } from "react-hook-form";
import { updateProfileImageAction } from "../_lib/actions";
import { UploadImage as UploadImageType } from "../_types/types";
import { useState } from "react";
import Button from "./Button";

function UploadImage() {
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UploadImageType>();

  async function onSubmit(data: UploadImageType) {
    try {
      await updateProfileImageAction(data);
    } catch (error) {
      if (error instanceof Error) setError("Image could not be uploaded.");
    } finally {
      reset();
    }
  }

  return (
    <form
      className="flex flex-col items-center gap-2 md:items-start"
      onSubmit={handleSubmit(onSubmit)}
    >
      <div className="flex w-48 justify-center md:block md:w-auto">
        <input
          type="file"
          accept="image/*"
          {...register("image", {
            required: "Please import an image.",
          })}
          className="w-full"
        />
      </div>
      <div className="flex w-full justify-center md:block md:w-auto">
        <Button type="secondary">Upload new image</Button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {errors.image && !error && (
        <p className="text-sm text-red-600">{errors.image.message}</p>
      )}
    </form>
  );
}

export default UploadImage;
