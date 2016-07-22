import java.util.Scanner;
public class Main{
	public static void main(String[] args){
		Scanner sc = new Scanner(System.in);
		int a = sc.nextInt();
		int b = sc.nextInt();
for(int i=0;i<1000000000;i++)for(int j=0;j<1000000000;j++){int aa=5; aa=aa/a; b+=aa;}
		System.out.printf("%d\n",a+b+1);
	}
}