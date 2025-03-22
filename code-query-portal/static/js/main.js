// Initialize highlight.js
document.addEventListener('DOMContentLoaded', function() {
  // Apply syntax highlighting to code blocks
  document.querySelectorAll('pre code').forEach((block) => {
      if (typeof hljs !== 'undefined') {
          hljs.highlightElement(block);
      } else {
          console.error('highlight.js is not loaded.');
      }
  });

  // Add animation to cards
  document.querySelectorAll('.card').forEach(card => {
      card.addEventListener('mouseenter', () => {
          card.style.transform = 'translateY(-5px)';
          card.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
      });
      
      card.addEventListener('mouseleave', () => {
          card.style.transform = 'translateY(0)';
          card.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
      });
  });

  // Auto-resize textareas
  document.querySelectorAll('textarea').forEach(textarea => {
      textarea.addEventListener('input', function() {
          this.style.height = 'auto';
          this.style.height = (this.scrollHeight) + 'px';
      });
  });
});