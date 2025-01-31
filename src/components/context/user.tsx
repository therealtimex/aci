"use client";

import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  useCallback,
  useEffect,
} from "react";
import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";

export interface User {
  userId: string;
  accessToken: string;
}

interface UserContextType {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  login: () => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => {
    const accessToken = Cookies.get("accessToken");

    let userId = null;

    if (accessToken) {
      try {
        const decodedToken: { sub: string } = jwtDecode(accessToken);
        userId = decodedToken.sub;
      } catch (error) {
        console.error("Failed to decode JWT token:", error);
      }
    }

    setUser(
      accessToken && userId
        ? {
            userId,
            accessToken,
          }
        : null
    );
  }, []);

  const login = useCallback(() => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/v1/auth/login/google/`;
  }, []);

  const logout = useCallback(() => {
    Cookies.remove("accessToken");
    setUser(null);
  }, [setUser]);

  return (
    <UserContext.Provider value={{ user, setUser, login, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
};
