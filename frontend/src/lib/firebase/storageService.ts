import { ref, uploadBytes, getDownloadURL, deleteObject } from "firebase/storage";
import { v4 as uuidv4 } from "uuid";
import { storage } from "./config";

export interface UploadedImage {
  url: string;
  path: string;
}

export async function uploadImage(file: File, userId: string): Promise<UploadedImage> {
  const fileExtension = file.name.split('.').pop();
  const fileName = `${uuidv4()}.${fileExtension}`;
  const path = `users/${userId}/wardrobe/${fileName}`;
  const storageRef = ref(storage, path);

  try {
    await uploadBytes(storageRef, file);
    const url = await getDownloadURL(storageRef);
    return { url, path };
  } catch (error) {
    console.error("Error uploading image:", error);
    throw error;
  }
}

export async function uploadMultipleImages(files: File[], userId: string): Promise<UploadedImage[]> {
  const uploadPromises = files.map(file => uploadImage(file, userId));
  return Promise.all(uploadPromises);
}

export async function deleteImage(path: string): Promise<void> {
  const storageRef = ref(storage, path);
  try {
    await deleteObject(storageRef);
  } catch (error) {
    console.error("Error deleting image:", error);
    throw error;
  }
}

export async function deleteMultipleImages(paths: string[]): Promise<void> {
  const deletePromises = paths.map(path => deleteImage(path));
  await Promise.all(deletePromises);
} 