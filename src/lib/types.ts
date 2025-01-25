export interface App {
    id: string;
    name: string;
    icon: string;
    description: string;
    categories: string[];
    tags: string[];
}

export interface AppFunction {
    id: string;
    name: string;
    functionId: string;
    description: string;
    categories: string[];
    tags: string[];
}
