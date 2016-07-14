#include<stdio.h>
int main(){
  int a, b;
  scanf("%d%d",&a,&b);
  a=1/0;
  printf("%d\n",a+b);
}