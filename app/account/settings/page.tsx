import UploadImage from "@/app/_components/UploadImage";
import { getProfile } from "@/app/_lib/data_service";
import { createClient } from "@/app/_lib/supabase/server";
import Image from "next/image";

async function Page() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user || !user.email) throw new Error("There is no user logged in.");
  const { firstName, lastName, image } = await getProfile(user.email);

  return (
    <div className="flex h-full w-full flex-col items-center justify-center py-8 lg:mt-8 lg:w-auto lg:items-start lg:justify-start">
      <div className="flex flex-col items-center gap-4 md:grid md:grid-cols-[auto_1fr]">
        <Image
          src={image ? image : "/noimage.jpg"}
          width={196}
          height={196}
          className="w-36 rounded-full"
          alt="Profile image"
        />
        <div className="flex flex-col justify-center gap-2 text-gray-600 dark:text-gray-300">
          <h2 className="text-center text-3xl font-semibold md:text-left">
            {firstName} {lastName}
          </h2>
          <div className="flex justify-center">
            <UploadImage />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Page;
