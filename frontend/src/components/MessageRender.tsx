import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MessageRendererProps {
  content: string;
  className?: string;
}

const MessageRenderer: React.FC<MessageRendererProps> = ({ content, className = '' }) => {
  return (
    <div className={`prose prose-sm max-w-none ${className}`}>
      <ReactMarkdown
        components={{
          // Custom code block renderer
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : 'text';
            
            return !inline ? (
              <SyntaxHighlighter
                style={oneDark}
                language={language}
                PreTag="div"
                className="rounded-lg"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className="inline-code" {...props}>
                {children}
              </code>
            );
          },
          // Custom paragraph renderer
          p({ children }: any) {
            return <p className="mb-2 last:mb-0">{children}</p>;
          },
          // Custom list renderers
          ul({ children }: any) {
            return <ul className="list-disc pl-4 mb-2">{children}</ul>;
          },
          ol({ children }: any) {
            return <ol className="list-decimal pl-4 mb-2">{children}</ol>;
          },
          li({ children }: any) {
            return <li className="mb-1">{children}</li>;
          },
          // Custom heading renderers
          h1({ children }: any) {
            return <h1 className="text-lg font-semibold mb-2 text-gray-900">{children}</h1>;
          },
          h2({ children }: any) {
            return <h2 className="text-base font-semibold mb-2 text-gray-900">{children}</h2>;
          },
          h3({ children }: any) {
            return <h3 className="text-sm font-semibold mb-1 text-gray-900">{children}</h3>;
          },
          // Custom blockquote renderer
          blockquote({ children }: any) {
            return (
              <blockquote className="border-l-4 border-primary-200 pl-4 italic text-gray-600 my-2">
                {children}
              </blockquote>
            );
          },
          // Custom table renderers
          table({ children }: any) {
            return (
              <div className="overflow-x-auto my-2">
                <table className="min-w-full border border-gray-200 rounded-lg">
                  {children}
                </table>
              </div>
            );
          },
          thead({ children }: any) {
            return <thead className="bg-gray-50">{children}</thead>;
          },
          tbody({ children }: any) {
            return <tbody className="divide-y divide-gray-200">{children}</tbody>;
          },
          tr({ children }: any) {
            return <tr>{children}</tr>;
          },
          th({ children }: any) {
            return (
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200 last:border-r-0">
                {children}
              </th>
            );
          },
          td({ children }: any) {
            return (
              <td className="px-3 py-2 text-sm text-gray-900 border-r border-gray-200 last:border-r-0">
                {children}
              </td>
            );
          },
          // Custom link renderer
          a({ href, children }: any) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-800 underline"
              >
                {children}
              </a>
            );
          },
          // Custom strong/bold renderer
          strong({ children }: any) {
            return <strong className="font-semibold text-gray-900">{children}</strong>;
          },
          // Custom em/italic renderer
          em({ children }: any) {
            return <em className="italic text-gray-700">{children}</em>;
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MessageRenderer;