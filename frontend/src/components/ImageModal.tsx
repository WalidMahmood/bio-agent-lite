import React from "react";
import { X, Download, ZoomIn } from "lucide-react";

interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  title: string;
}

export const ImageModal: React.FC<ImageModalProps> = ({
  isOpen,
  onClose,
  imageUrl,
  title
}) => {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={title || "Image Preview"}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="relative max-w-4xl w-full max-h-[90vh] bg-[#0c1210] border border-white/20 rounded-2xl overflow-hidden shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between bg-black/40">
          <div className="flex items-center gap-2">
            <ZoomIn className="w-4 h-4 text-[#14BE8A]" />
            <h3 className="text-sm font-semibold text-white">{title}</h3>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={imageUrl}
              download={title.toLowerCase().replace(/\s+/g, "_") + ".png"}
              className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/10 hover:bg-white/15 text-xs text-white transition"
              title="Download image at high resolution"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PNG</span>
            </a>

            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Image Body */}
        <div className="p-4 flex items-center justify-center overflow-auto bg-black/60">
          <img
            src={imageUrl}
            alt={title}
            className="max-h-[75vh] w-auto object-contain rounded-lg shadow-lg border border-white/5"
          />
        </div>
      </div>
    </div>
  );
};
