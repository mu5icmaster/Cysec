import { FiltersType, Product, Profile } from "../_types/types";
import { Order } from "../_types/types";
import { PRODUCTS_PER_PAGE } from "./constants";
import { createClient } from "./supabase/server";
import { createClient as createSupabaseClient } from "./supabase/client";

// Client instance of SUPABASE
const supabaseClient = createSupabaseClient();

export async function getProducts(
  searchValue?: string | undefined,
  page?: number,
  filters?: FiltersType,
  sort?: "relevant" | "highest" | "lowest",
): Promise<{ data: Product[]; count: number }> {
  let query = supabaseClient.from("products").select("*");
  let countQuery = supabaseClient
    .from("products")
    .select("*", { count: "exact", head: true });

  if (searchValue) {
    query = query.or(
      `brand.ilike.%${searchValue}%,product_name.ilike.%${searchValue}%`,
    );
    countQuery = countQuery.or(
      `brand.ilike.%${searchValue}%,product_name.ilike.%${searchValue}%`,
    );
  }

  // filtering by category
  if (filters?.categories?.length) {
    query = query.in("category", filters?.categories);
    countQuery = countQuery.in("category", filters?.categories);
  }

  // filtering by brand
  if (filters?.brands?.length) {
    query = query.in("brand", filters.brands);
    countQuery = countQuery.in("brand", filters?.brands);
  }

  // filtering by price
  if (filters?.price) {
    query = query.gt("final_price", filters.price.min);
    query = query.lt("final_price", filters.price.max);
    countQuery = countQuery.gt("final_price", filters.price.min);
    countQuery = countQuery.lt("final_price", filters.price.max);
  }

  // sorting
  if (sort) {
    switch (sort) {
      case "highest":
        query.order("final_price", { ascending: false });
        break;
      case "lowest":
        query.order("final_price", { ascending: true });
        break;
    }
  }

  const { count } = await countQuery;

  if (page) {
    const from = (page - 1) * PRODUCTS_PER_PAGE;
    const to = from + PRODUCTS_PER_PAGE - 1;

    if (from > Number(count) - 1) query = query.range(0, PRODUCTS_PER_PAGE - 1);
    else query = query.range(from, to);
  }

  const { data, error } = await query;

  if (error) throw new Error(error.message);
  if (!data) return { data: [], count: count ?? 0 };

  return { data, count: count ?? 0 };
}

export async function getBrands(): Promise<string[]> {
  const { data, error } = await supabaseClient.from("products").select("brand");

  if (error || !data) throw new Error(error.message);

  const brands = Array.from(new Set(data.map((brand) => brand.brand)));

  return brands;
}

export async function getCategories(): Promise<string[]> {
  const { data, error } = await supabaseClient
    .from("products")
    .select("category");

  if (error) throw new Error(error.message);
  if (!data) return [];

  const categories = Array.from(new Set(data.map((cat) => cat.category)));

  return categories;
}

export async function getProductById(id: number): Promise<Product> {
  const { data, error } = await supabaseClient
    .from("products")
    .select("*")
    .eq("id", id)
    .single();

  if (error) throw new Error(error.message);

  return data;
}

export async function getProductsByIds(ids: number[]): Promise<Product[]> {
  const { data, error } = await supabaseClient
    .from("products")
    .select("*")
    .in("id", ids);

  if (error) throw new Error(error.message);
  return data;
}

export async function getBestsellers(): Promise<Product[]> {
  const { data, error } = await supabaseClient
    .from("bestsellers")
    .select(`products(*)`);

  if (error) throw new Error(error.message);
  if (!data) throw new Error("There are not any bestsellers.");

  return data.flatMap((prod) => prod.products);
}

export async function getProductsByCategory(
  category: string,
): Promise<Product[]> {
  const { data, error } = await supabaseClient
    .from("products")
    .select("*")
    .eq("category", category);

  if (error) throw new Error(error.message);
  if (!data || !data.length) throw new Error("No products in this category :(");

  return data;
}

// WITH NEED OF AUTHORIZATION
export async function getProfile(email: string): Promise<Profile> {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("profiles")
    .select("email, image, firstName, lastName")
    .eq("email", email)
    .single();

  if (error) throw new Error(error.message);
  if (!data) throw new Error("Profile not found.");

  return data;
}

export async function getUserOrders(): Promise<Order[]> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) throw new Error("There is no user logged in.");

  const { data: ordersData, error: orderError } = await supabase
    .from("orders")
    .select("id, total_price, status, address, first_name, last_name")
    .eq("user_id", user.id);

  if (orderError) throw new Error("No orders found.");

  const orderIds = ordersData.map((order) => order.id);

  const { data: orderItemsData, error: itemsError } = await supabase
    .from("order_items")
    .select("product_id, quantity, order_id")
    .in("order_id", orderIds);

  if (itemsError) throw new Error("No orders found.");

  const finalOrders = ordersData.map((o) => {
    const items = orderItemsData
      .filter((item) => item.order_id === o.id)
      .map((item) => {
        return { product_id: item.product_id, quantity: item.quantity };
      });

    return { ...o, items };
  });

  if (finalOrders.length === 0) throw new Error("No orders found.");

  return finalOrders;
}

export async function getOrderDetails(id: string): Promise<Order> {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user?.email) throw new Error("There is no user logged in.");

  const { data: ordersData, error: orderError } = await supabase
    .from("orders")
    .select("id, total_price, status, address, first_name, last_name")
    .eq("id", id)
    .single();

  if (orderError) throw new Error("Order not found.");

  const { data: orderItemsData, error: itemsError } = await supabase
    .from("order_items")
    .select("product_id, quantity, order_id")
    .eq("order_id", id);

  if (itemsError) throw new Error("Order not found.");
  const finalOrder = { ...ordersData, items: orderItemsData };

  return finalOrder;
}

export async function createProfile(newProfile: Profile): Promise<void> {
  const supabase = await createClient();
  const { error } = await supabase.from("profiles").insert([{ ...newProfile }]);

  if (error) throw new Error("Profile could not be created");
}
