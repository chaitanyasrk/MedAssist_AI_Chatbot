import { useEffect, useRef } from 'react';

export function useAutoScroll<T extends HTMLElement>(
  dependency: any,
  enabled: boolean = true
) {
  const elementRef = useRef<T>(null);

  useEffect(() => {
    if (enabled && elementRef.current) {
      const element = elementRef.current;
      const scrollHeight = element.scrollHeight;
      const height = element.clientHeight;
      const maxScrollTop = scrollHeight - height;
      
      // Only scroll if user is near the bottom
      if (element.scrollTop > maxScrollTop - 100) {
        element.scrollTo({
          top: scrollHeight,
          behavior: 'smooth'
        });
      }
    }
  }, [dependency, enabled]);

  return elementRef;
}