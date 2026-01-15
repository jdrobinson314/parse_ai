# Generate a large markdown file with many code blocks
import sys

def main():
    filename = "output/stress_test.md"
    num_blocks = 1500
    
    print(f"Generating {filename} with {num_blocks} blocks...")
    
    with open(filename, 'w') as f:
        f.write("# Stress Test\n\nThis file contains many code blocks.\n\n")
        
        for i in range(1, num_blocks + 1):
            f.write(f"### Block {i}\n")
            f.write(f"```python\n")
            f.write(f"def func_{i}():\n")
            f.write(f"    print('This is block {i}')\n")
            f.write(f"```\n\n")

    print("Done.")

if __name__ == "__main__":
    main()
