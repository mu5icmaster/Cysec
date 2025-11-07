"use server";
import { redirect } from "next/navigation";
import {
  OrderForm,
  SignUpFormValues,
  UploadImage,
  LoginFormValues,
} from "../_types/types";
import { createProfile } from "./data_service";
import { revalidatePath } from "next/cache";
import { SHIPPING_COST, SUPABASE_URL } from "./constants";
import { createClient } from "./supabase/server";

export async function loginAction(data: LoginFormValues) {
  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword(data);

  if (error) throw new Error(error.message);

  revalidatePath("/account/*");
}

export async function signOutAction() {
  const supabase = await createClient();
  const { error } = await supabase.auth.signOut();

  if (error) throw new Error(error.message);
  redirect("/login");
}

export async function signUpAction(data: SignUpFormValues) {
  const supabase = await createClient();
  const { email, password, firstName, lastName } = data;
  const { data: userData, error } = await supabase.auth.signUp({
    email,
    password,
  });

  const profile = {
    firstName,
    lastName,
    email,
    image: "",
    user_id: userData.user?.id,
  };

  if (error) throw new Error(error.message);
  await createProfile(profile);
  redirect("/login");
}

export async function updateProfileImageAction(data: UploadImage) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { image } = data;
  const img = Array.isArray(image) ? image.at(0) : image;

  if (!user || !user.email) throw new Error("There is no user logged in.");

  const imageName = `${Math.random()}-${user.email}-${img.name}`;
  const imagePath = `${SUPABASE_URL}/storage/v1/object/public/profile_images/${imageName}`;

  const { error } = await supabase
    .from("profiles")
    .update({ image: imagePath })
    .eq("email", user.email);

  if (error) throw new Error("Image could not be uploaded.");

  const { error: storageErr } = await supabase.storage
    .from("profile_images")
    .upload(imageName, img, {
      cacheControl: "3600",
      upsert: false,
    });

  if (storageErr) {
    await supabase
      .from("profiles")
      .update({ image: "" })
      .eq("email", user.email);
    throw new Error("Image could not be uploaded.");
  }

  revalidatePath("/account/*");
}

export async function createOrderAction(orderData: OrderForm) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user || !user?.email)
    throw new Error("You have to be signed in to place the order.");

  const ids = orderData.products.map((prod) => prod.id);

  // double checking prices with database
  const { data, error } = await supabase
    .from("products")
    .select("id, regular_price, discount")
    .in("id", ids);

  const products = data?.map((prod) => {
    const { quantity } = orderData.products.find(
      (cartProd) => cartProd.id === prod.id,
    )!;

    return { ...prod, quantity };
  });

  if (error)
    throw new Error(
      "There was a problem with getting products prices. Try again later.",
    );

  const price = products?.reduce((acc, cur) => {
    const regularPrice = cur.regular_price * cur.quantity;
    const discounts = Number(cur.discount) * cur.quantity;

    return (acc += regularPrice - discounts);
  }, 0);

  const totalPrice = Number(price) + SHIPPING_COST;

  const orderID = Date.now();

  const finalOrder = {
    id: orderID,
    total_price: totalPrice,
    status: "pending",
    email: user.email,
    address: `${orderData.postal_code} ${orderData.city} ${orderData.address}`,
    user_id: user.id,
  };

  const finalProducts = products?.map((prod) => {
    return {
      product_id: prod.id,
      quantity: prod.quantity,
      order_id: orderID,
      user_id: user.id,
    };
  });

  const { error: finalOrderError } = await supabase
    .from("orders")
    .insert(finalOrder);

  if (finalOrderError) {
    throw new Error("There is a problem with creating new order.");
  }

  const { error: productsError } = await supabase
    .from("order_items")
    .insert(finalProducts);

  if (productsError)
    throw new Error("There is a problem with creating new order.");

  redirect(`/thankyou`);
}

export async function cancelOrderAction(id: string) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) throw new Error("There is no user logged in.");

  const { data: itemsData, error: itemsError } = await supabase
    .from("order_items")
    .delete()
    .eq("order_id", id)
    .select();
  if (itemsError || !itemsData.length)
    throw new Error("Order couldn't be canceled.");

  const { data: orderData, error: orderError } = await supabase
    .from("orders")
    .delete()
    .eq("id", id)
    .select();
  if (orderError || !orderData.length)
    throw new Error("Order couldn't be canceled.");

  revalidatePath("/account/orders");
  redirect("/account/orders");
}
