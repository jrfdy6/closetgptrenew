import { useState } from "react";
import {
  collection,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  query,
  where,
  getDocs,
  DocumentData,
  Query,
} from "firebase/firestore";
import { db } from "../firebase/config";

export function useFirestore(collectionName: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const addDocument = async (data: DocumentData) => {
    if (!db) {
      throw new Error("Firestore is not initialized");
    }
    setLoading(true);
    setError(null);

    try {
      const docRef = await addDoc(collection(db, collectionName), {
        ...data,
        createdAt: new Date().toISOString(),
      });
      return docRef.id;
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to add document");
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateDocument = async (id: string, data: DocumentData) => {
    if (!db) {
      throw new Error("Firestore is not initialized");
    }
    setLoading(true);
    setError(null);

    try {
      const docRef = doc(db, collectionName, id);
      await updateDoc(docRef, {
        ...data,
        updatedAt: new Date().toISOString(),
      });
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to update document");
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (id: string) => {
    if (!db) {
      throw new Error("Firestore is not initialized");
    }
    setLoading(true);
    setError(null);

    try {
      const docRef = doc(db, collectionName, id);
      await deleteDoc(docRef);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to delete document");
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getDocuments = async (conditions: { field: string; operator: string; value: any }[] = []) => {
    if (!db) {
      throw new Error("Firestore is not initialized");
    }
    setLoading(true);
    setError(null);

    try {
      const collectionRef = collection(db, collectionName);
      let q: Query<DocumentData>;
      
      if (conditions.length > 0) {
        q = query(
          collectionRef,
          ...conditions.map(({ field, operator, value }) => where(field, operator as any, value))
        );
      } else {
        q = query(collectionRef);
      }

      const querySnapshot = await getDocs(q);
      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
      }));
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to get documents");
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    addDocument,
    updateDocument,
    deleteDocument,
    getDocuments,
    loading,
    error,
  };
} 