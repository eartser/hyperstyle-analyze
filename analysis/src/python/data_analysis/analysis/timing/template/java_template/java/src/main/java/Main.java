import java.util.Scanner;
class Main {
    public static void main(String[] args) {
        // put your code here
         Scanner scanner = new Scanner(System.in);

        int a = scanner.nextInt();
        int b = scanner.nextInt();

        int product = 1;
        for (int i = a; i <= b; i++) {
            product = i;
            if (product % 3 == 0 && product % 5 == 0) {
                System.out.println("FizzBuzz");
            } else if (product % 3 == 0) {
                System.out.println("Fizz");
            } else if (product % 5 == 0) {
                System.out.println("Buzz");
            } else {
                System.out.println(product);
            }
        }    
    }
}
