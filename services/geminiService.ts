import { GoogleGenAI, Type } from "@google/genai";
import { SYSTEM_INSTRUCTION } from "../constants";

export const generateTradingScript = async (
  userPrompt: string
): Promise<string> => {
  try {
    const apiKey = process.env.API_KEY;
    if (!apiKey) {
      throw new Error("API Key not found");
    }

    const ai = new GoogleGenAI({ apiKey });

    // We use gemini-3-pro-preview for complex coding tasks
    const modelId = "gemini-3-pro-preview";

    const response = await ai.models.generateContent({
      model: modelId,
      contents: userPrompt,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        temperature: 0.2, // Low temperature for precise code generation
        maxOutputTokens: 8000,
        // thinkingConfig: { thinkingBudget: 1024 } // Optional: enable for complex logic if needed
      },
    });

    return response.text || "# Error generating code. Please try again.";
  } catch (error) {
    console.error("Gemini API Error:", error);
    throw error;
  }
};

export const explainCode = async (code: string): Promise<string> => {
  try {
    const apiKey = process.env.API_KEY;
    if (!apiKey) return "API Key missing.";

    const ai = new GoogleGenAI({ apiKey });
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: `Explain the key logic flow of this Python trading script in simple bullet points, focusing on the entry conditions and risk management:\n\n${code.substring(0, 5000)}`,
    });
    
    return response.text || "No explanation generated.";
  } catch (error) {
    return "Failed to generate explanation.";
  }
};
