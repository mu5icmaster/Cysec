import type { Metadata } from "next";
import { getProfile } from "../_lib/data_service";
import Image from "next/image";
import { createClient } from "../_lib/supabase/server";

export const metadata: Metadata = {
  title: "Account",
};

async function Page() {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user || !user.email) throw new Error("There is no user logged in.");
  const { email, firstName, image } = await getProfile(user.email);

  return (
    <div className="flex h-full w-full flex-col items-center justify-center py-8 md:mt-8 md:items-start md:justify-start lg:w-auto">
      <div className="grid gap-8 md:grid-cols-[auto_1fr]">
        <Image
          src={image ? image : "/noimage.jpg"}
          width={196}
          height={196}
          alt="Profile image"
          className="rounded-full"
        />
        <div className="flex flex-col justify-center gap-2 text-gray-600 dark:text-gray-300">
          <h2 className="text-center text-4xl font-semibold md:text-left">
            Hello {firstName}!
          </h2>
          <div className="flex flex-col text-xl">
            <p className="text-center md:text-left">{email}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Page;
